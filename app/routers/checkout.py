
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import requests
import os

from ..database import get_db
from ..models import Order, OrderItem, Product, Vendor, User
from ..dep.security import get_current_user
from ..config import settings
from pydantic import BaseModel

router = APIRouter(prefix="/checkout", tags=["Orders & Payments"])

# ==============================
# ✅ PAYSTACK CONFIG
# ==============================
PAYSTACK_SECRET_KEY = os.getenv(
    "PAYSTACK_SECRET_KEY", "sk_test_3e95cf7e607da264fecc599fe380ac04e217944c"
)
PAYSTACK_BASE_URL = os.getenv("PAYSTACK_BASE_URL", "https://api.paystack.co")


# ==============================
# 🧾 SCHEMAS
# ==============================
class ProductTypeData(BaseModel):
    id: int
    type_value: str
    value_measurement: str
    value_price: float
    quantity: int


class CheckoutItem(BaseModel):
    productId: int
    vendor: int
    type: ProductTypeData
    quantity: int
    price: float
    discountPrice: float


class CheckoutRequest(BaseModel):
    amount: float
    checkouts: List[CheckoutItem]


class PaymentInitResponse(BaseModel):
    status: bool
    message: str
    authorization_url: Optional[str]
    reference: Optional[str]


class PaymentVerifyResponse(BaseModel):
    status: bool
    message: str
    order_status: Optional[str] = None
    reference: Optional[str] = None


# ==============================
# 🛒 INITIATE CHECKOUT
# ==============================
@router.post("/", response_model=PaymentInitResponse)
def initiate_checkout(
    body: CheckoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create an order, order items, and initialize Paystack payment.
    """

    # 1️⃣ Create order record
    new_order = Order(
        user_id=current_user.id,
        total_amount=body.amount,
        status="pending",
        created_at=datetime.utcnow(),
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # 2️⃣ Create order items
    for item in body.checkouts:
        subtotal = item.discountPrice * item.quantity  # ✅ calculate subtotal

        db_item = OrderItem(
            order_id=new_order.id,
            product_id=item.productId,
            vendor_id=item.vendor,
            quantity=item.quantity,
            price=item.price,
            discount_price=item.discountPrice,
            type_id=item.type.id,
            subtotal=subtotal,  # ✅ store subtotal
        )
        db.add(db_item)

    db.commit()

    # 3️⃣ Initialize payment with Paystack
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    reference = f"ORDER_{new_order.id}_{int(datetime.utcnow().timestamp())}"

    payload = {
        "email": current_user.email,
        "amount": int(body.amount * 100),  # Paystack expects amount in kobo
        "reference": reference,
        "callback_url": "https://aquasense-backend-jsa5.onrender.com/api/v1/checkout/payment/verify",
    }

    response = requests.post(
        f"{PAYSTACK_BASE_URL}/transaction/initialize",
        json=payload,
        headers=headers,
    )

    res_data = response.json()

    if not res_data.get("status"):
        raise HTTPException(
            status_code=400,
            detail=res_data.get("message", "Payment initialization failed"),
        )

    # Save reference to DB
    new_order.reference = res_data["data"]["reference"]
    db.commit()

    return PaymentInitResponse(
        status=True,
        message="Payment initialized successfully",
        authorization_url=res_data["data"]["authorization_url"],
        reference=res_data["data"]["reference"],
    )


# ==============================
# 🔍 VERIFY PAYMENT
# ==============================
@router.get("/verify/{reference}", response_model=PaymentVerifyResponse)
def verify_payment(reference: str, db: Session = Depends(get_db)):
    """
    Verify Paystack transaction and update order status.
    """
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}
    verify_url = f"{PAYSTACK_BASE_URL}/transaction/verify/{reference}"

    response = requests.get(verify_url, headers=headers)
    res_data = response.json()

    if not res_data.get("status"):
        raise HTTPException(
            status_code=400,
            detail=res_data.get("message", "Unable to verify payment"),
        )

    # Get payment data
    data = res_data.get("data", {})
    payment_status = data.get("status")

    # Find order
    order = db.query(Order).filter(Order.reference == reference).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Update status
    if payment_status == "success":
        order.status = "paid"
    else:
        order.status = "failed"

    db.commit()

    return PaymentVerifyResponse(
        status=True,
        message="Payment verification complete",
        order_status=order.status,
        reference=reference,
    )
