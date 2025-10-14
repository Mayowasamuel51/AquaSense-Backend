import os
import requests
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Product, ProductType, Transaction
from ..dep.security import get_current_user

router = APIRouter(prefix="/checkout", tags=["checkout"])

# -------------------------------
# Config
# -------------------------------
PAYSTACK_SECRET_KEY = os.getenv(
    "PAYSTACK_SECRET_KEY", "sk_test_3e95cf7e607da264fecc599fe380ac04e217944c"
)
PAYSTACK_BASE_URL = os.getenv("PAYSTACK_BASE_URL", "https://api.paystack.co")

COINS_PER_ITEM = 100        # 100 coins allowed per item
NAIRA_PER_100_COINS = 500   # 100 coins = ₦500 discount

# -------------------------------
# Schemas
# -------------------------------
class CheckoutItem(BaseModel):
    product_id: int
    product_type_id: Optional[int] = None   # if buying a variant
    unit_price: float
    quantity: int
    coins_used: int
    subtotal: float

class CheckoutPayload(BaseModel):
    items: List[CheckoutItem]
    total_before_discount: float
    total_discount: float
    total_after_discount: float

# -------------------------------
# Paystack helper
# -------------------------------
def initialize_paystack(email: str, amount: int):
    url = f"{PAYSTACK_BASE_URL}/transaction/initialize"
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}
    payload = {"email": email, "amount": amount * 100}  # Naira → Kobo

    res = requests.post(url, json=payload, headers=headers)
    if res.status_code != 200:
        raise HTTPException(status_code=400, detail="Paystack init failed")

    return res.json()["data"]

# -------------------------------
# Checkout endpoint
# -------------------------------
@router.post("/")
def checkout(
    order: CheckoutPayload,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    total_discount_calculated = 0
    coins_needed = 0
    total_from_products = 0
    db_user = db.query(User).filter(User.id == user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # 🔹 Step 1: Verify each product against DB
    for item in order.items:
        db_product = db.query(Product).filter(Product.id == item.product_id).first()
        if not db_product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")

        # 🔹 Check if it's a typed product
        if db_product.types:
            db_type = db.query(ProductType).filter(
                ProductType.product_id == item.product_id
            ).first()

            if not db_type:
                raise HTTPException(status_code=404, detail="Product type not found")

            if db_type.quantity < item.quantity:
                raise HTTPException(status_code=400, detail="Not enough stock for this product type")
        else:
            # 🔹 Check product-level stock
            if db_product.quantity < item.quantity:
                raise HTTPException(status_code=400, detail="Not enough stock for this product")

    # 🔹 Step 3: Validate totals from frontend
    if total_from_products != order.total_before_discount:
        raise HTTPException(status_code=400, detail="Price mismatch in request")

    if user.coin_caps < coins_needed:
        raise HTTPException(status_code=400, detail="Not enough coins in wallet")

    expected_total = order.total_before_discount - total_discount_calculated
    if expected_total != order.total_after_discount:
        raise HTTPException(status_code=400, detail="Totals mismatch")

    # 🔹 Step 4: Deduct coins
    user.coin_caps -= coins_needed
    db.commit()

    # 🔹 Step 5: Create transaction record
    transaction = Transaction(
        user_id=user.id,
        total_amount=order.total_before_discount,
        coins_used=coins_needed,
        discount=total_discount_calculated,
        final_amount=expected_total,
        status="pending",
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    # 🔹 Step 6: Handle Paystack or mark as success
    if expected_total > 0:
        paystack_data = initialize_paystack(user.email, expected_total)
        transaction.paystack_ref = paystack_data["reference"]
        db.commit()
        return {
            "message": "Partially paid with coins. Complete with Paystack.",
            "status": "pending",
            "coins_used": coins_needed,
            "discount": total_discount_calculated,
            "amount_to_pay": expected_total,
            "paystack": paystack_data,
            "transaction_id": transaction.id,
        }

    # Fully paid with coins → mark success + reduce stock
    transaction.status = "success"
    db.commit()

    for item in order.items:
        if item.product_type_id:
            db_type = db.query(ProductType).filter(ProductType.id == item.product_type_id).first()
            db_type.quantity -= item.quantity
        else:
            db_product = db.query(Product).filter(Product.id == item.product_id).first()
            db_product.quantity -= item.quantity
    db.commit()

    return {
        "message": "Paid fully with coins",
        "status": "success",
        "coins_used": coins_needed,
        "discount": total_discount_calculated,
        "amount_to_pay": 0,
        "transaction_id": transaction.id,
    }

@router.get("/verify/{reference}")
def verify_payment(reference: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """
    Verify Paystack payment after user completes transaction.
    """
    # 🔹 Find transaction
    transaction = db.query(Transaction).filter(
        Transaction.paystack_ref == reference,
        Transaction.user_id == user.id
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if transaction.status == "success":
        return {"message": "Payment already verified", "transaction_id": transaction.id}

    # 🔹 Call Paystack API
    url = f"{PAYSTACK_BASE_URL}/transaction/verify/{reference}"
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}
    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        raise HTTPException(status_code=400, detail="Paystack verification failed")

    data = res.json()
    if data["data"]["status"] != "success":
        raise HTTPException(status_code=400, detail="Payment not successful")

    # 🔹 Update transaction
    transaction.status = "success"
    db.commit()

    # 🔹 Deduct stock now that payment is confirmed
    # (Assuming you have a TransactionItem table or store items in payload JSON)
    # For now, I’ll show inline approach if you store `items_json` in Transaction
    if hasattr(transaction, "items_json") and transaction.items_json:
        for item in transaction.items_json:
            if item["product_type_id"]:
                db_type = db.query(ProductType).filter(ProductType.id == item["product_type_id"]).first()
                if db_type and db_type.quantity >= item["quantity"]:
                    db_type.quantity -= item["quantity"]
            else:
                db_product = db.query(Product).filter(Product.id == item["product_id"]).first()
                if db_product and db_product.quantity >= item["quantity"]:
                    db_product.quantity -= item["quantity"]
        db.commit()

    return {
        "message": "Payment verified successfully",
        "status": "success",
        "transaction_id": transaction.id,
        "final_amount": transaction.final_amount
    }
