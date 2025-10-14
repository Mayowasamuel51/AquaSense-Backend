from fastapi import APIRouter, Depends, HTTPException , Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import requests
import os
import hmac
import hashlib
# import requests

from starlette.responses import JSONResponse, HTMLResponse

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
    "PAYSTACK_SECRET_KEY",
    "sk_test_3e95cf7e607da264fecc599fe380ac04e217944c"
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


# ==============================
# 🛒 INITIATE CHECKOUT
# ==============================
@router.post("/")
def initiate_checkout(
    body: CheckoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create an order, add items, and initialize Paystack payment.
    """

    # 1️⃣ Create Order
    new_order = Order(
        user_id=current_user.id,
        total_amount=body.amount,
        status="pending",
        created_at=datetime.utcnow(),
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # 2️⃣ Add Order Items
    for item in body.checkouts:
        subtotal = item.discountPrice * item.quantity

        db_item = OrderItem(
            order_id=new_order.id,
            product_id=item.productId,
            vendor_id=item.vendor,
            quantity=item.quantity,
            price=item.price,
            discount_price=item.discountPrice,
            type_id=item.type.id,
            subtotal=subtotal,
        )
        db.add(db_item)
    db.commit()

    # 3️⃣ Initialize Payment (no manual reference)
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "email": current_user.email,
        "amount": int(body.amount * 100),  # Paystack needs amount in kobo
        # "callback_url":"https://aquasense-backend-jsa5.onrender.com/api/v1/paystack/webhook"
        # "callback_url": "https://aquasense-backend-jsa5.onrender.com/api/v1/checkout/verify",
        "callback_url": "https://aquasense-backend-jsa5.onrender.com/api/v1/checkout/paystack/callback"
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

    # 4️⃣ Save Paystack reference in DB
    paystack_ref = res_data["data"]["reference"]
    new_order.payment_reference = paystack_ref
    db.commit()

    # 5️⃣ Return clean response
    return {
        "message": "Order created. Proceed to Paystack payment.",
        "authorization_url": res_data["data"]["authorization_url"],
        "reference": paystack_ref,
        "order_id": new_order.id,
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "profilepicture": getattr(current_user, "profilepicture", None),
            "phone": getattr(current_user, "phone", None),
            "kyc_status": getattr(current_user, "kyc_status", "unverified"),
            "emailverified": getattr(current_user, "emailverified", True),
        },
    }


# ==============================
# 🔍 VERIFY PAYMENT
# ==============================
@router.get("/verify/{reference}")
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

    data = res_data.get("data", {})
    payment_status = data.get("status")

    # 🔍 Find the order by Paystack reference
    order = db.query(Order).filter(Order.payment_reference == reference).first()
    if not order:
        raise HTTPException(status_code=404, detail="Transaction reference not found.")

    # ✅ Update status
    if payment_status == "success":
        order.status = "paid"
    else:
        order.status = "failed"

    db.commit()

    return {
        "status": True,
        "message": "Payment verification complete",
        "order_status": order.status,
        "reference": reference,
    }





@router.get("/paystack/callback")
def paystack_callback(reference: str, request: Request, db: Session = Depends(get_db)):
    """Callback URL that Paystack redirects to after payment"""
    verify_url = f"{PAYSTACK_BASE_URL}/transaction/verify/{reference}"
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}
    res = requests.get(verify_url, headers=headers)
    data = res.json()
    lab = db.query(Order).filter(Order.payment_reference == reference).first()
    if not lab:
        raise HTTPException(status_code=404, detail="Lab order not found")
    status = data.get("data", {}).get("status", "failed")
    amount_paid = data.get("data", {}).get("amount", 0) / 100
    channel = data.get("data", {}).get("channel", "unknown")
    gateway_response = data.get("data", {}).get("gateway_response", "")
    currency = data.get("data", {}).get("currency", "NGN")

    # ✅ Update payment status
    if status == "success":
        lab.payment_status = "success"
    elif status == "failed":
        lab.payment_status = "failed"
    else:
        lab.payment_status = "pending"
    db.commit()

    # ✅ Prepare response data
    response_data = {
        "success": True,
        "message": "Payment verification completed",
        "payment_status": status,
        "lab_order": {
            "id": lab.id,
            "totalPrice": lab.totalPrice,
            "payment_status": lab.payment_status,
            "payment_method": lab.payment_method,
            "transaction_reference": lab.transaction_reference,
        },
        "paystack": {
            "amount_paid": amount_paid,
            "channel": channel,
            "currency": currency,
            "gateway_response": gateway_response,
        }
    }

    # ✅ Detect client type (browser or API)
    accept_header = request.headers.get("accept", "")

    if "text/html" in accept_header:
        # Return HTML view if opened in a browser
        html = f"""
        <html>
          <head><title>Payment {status.title()}</title></head>
          <body style="text-align:center; font-family: Arial; margin-top:50px;">
            <h2>Payment Status: <span style="color:{'green' if status == 'success' else 'red'}">{status.upper()}</span></h2>
            <p>Reference: <b>{reference}</b></p>
            <p>Amount: ₦{amount_paid:,.2f}</p>
            <p>Payment Method: {channel}</p>
            <p>Gateway Response: {gateway_response}</p>
            <br>
            <p>Thank you for your order!</p>
          </body>
        </html>
        """
        return HTMLResponse(content=html)

    # Otherwise return JSON (for mobile clients or frontend API)
    return JSONResponse(content=response_data)

@router.post("/webhook")
async def paystack_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle Paystack payment webhook.
    Verifies signature and updates order automatically.
    """
    payload = await request.body()
    signature = request.headers.get("x-paystack-signature")

    # Verify Paystack signature
    computed_signature = hmac.new(
        PAYSTACK_SECRET_KEY.encode("utf-8"),
        msg=payload,
        digestmod=hashlib.sha512
    ).hexdigest()

    if signature != computed_signature:
        raise HTTPException(status_code=400, detail="Invalid Paystack signature")

    data = await request.json()
    event = data.get("event")
    event_data = data.get("data", {})

    # ✅ Get reference
    reference = event_data.get("reference")
    order = db.query(Order).filter(Order.payment_reference == reference).first()

    if not order:
        return JSONResponse(
            status_code=404,
            content={"message": "Order not found for reference."}
        )

    # ✅ Handle payment events
    if event == "charge.success":
        order.status = "paid"
    elif event in ["charge.failed", "payment.failed"]:
        order.status = "failed"
    elif event == "refund.processed":
        order.status = "refunded"

    db.commit()

    return JSONResponse(
        status_code=200,
        content={"message": f"Webhook processed: {event}", "status": order.status}
    )