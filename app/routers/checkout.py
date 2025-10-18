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
from ..models import Order, OrderItem, Product, Vendor, User, DeliveryAddress
from ..dep.security import get_current_user
from ..config import settings
from pydantic import BaseModel

router = APIRouter(prefix="/checkout", tags=["Orders & Payments"])
#
# # ==============================
# # ✅ PAYSTACK CONFIG
# # ==============================
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
    delivery_address_id: int
    checkouts: List[CheckoutItem]

class DeliveryInfo(BaseModel):
    recipient_name: str
    phone_number: str
    address: str
    city: str
    state: str
    postal_code: Optional[str] = None
    delivery_instructions: Optional[str] = None


@router.post("/")
def initiate_checkout(
    body: CheckoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create an order linked to a saved delivery address, add items, and initialize Paystack payment.
    """
    # ✅ 1. Verify delivery address belongs to user
    delivery_address = db.query(DeliveryAddress).filter(
        DeliveryAddress.id == body.delivery_address_id,
        DeliveryAddress.user_id == current_user.id
    ).first()

    if not delivery_address:
        raise HTTPException(
            status_code=404,
            detail="Invalid delivery address or not associated with current user."
        )

    # ✅ 2. Create Order (link to delivery_address_id)
    new_order = Order(
        user_id=current_user.id,
        total_amount=body.amount,
        status="pending",
        created_at=datetime.utcnow(),
        delivery_address_id=delivery_address.id,
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # ✅ 3. Add Order Items
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

    # ✅ 4. Initialize Paystack
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "email": current_user.email,
        "amount": int(body.amount * 100),
        "callback_url": "https://aquasense-backend-jsa5.onrender.com/api/v1/checkout/paystack/callback"
    }

    response = requests.post(f"{PAYSTACK_BASE_URL}/transaction/initialize", json=payload, headers=headers)
    res_data = response.json()

    if not res_data.get("status"):
        raise HTTPException(status_code=400, detail=res_data.get("message", "Payment initialization failed"))

    paystack_ref = res_data["data"]["reference"]
    new_order.payment_reference = paystack_ref
    db.commit()

    # ✅ 5. Return response
    return {
        "message": "Order created. Proceed to Paystack payment.",
        "authorization_url": res_data["data"]["authorization_url"],
        "reference": paystack_ref,
        "order_id": new_order.id,
        "delivery_address": {
            "id": delivery_address.id,
            "recipient_name": delivery_address.recipient_name,
            "phone_number": delivery_address.phone_number,
            "address": delivery_address.address,
            "city": delivery_address.city,
            "state": delivery_address.state,
            "postal_code": delivery_address.postal_code,
            "delivery_instructions": delivery_address.delivery_instructions,
        },
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
        },
    }
# # ==============================
# # 🛒 INITIATE CHECKOUT
# # ==============================
# @router.post("/")
# def initiate_checkout(
#     body: CheckoutRequest,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     """
#     Create an order, add items, and initialize Paystack payment.
#     """
#
#     # 1️⃣ Create Order
#     new_order = Order(
#         user_id=current_user.id,
#         total_amount=body.amount,
#         status="pending",
#         created_at=datetime.utcnow(),
#     )
#     db.add(new_order)
#     db.commit()
#     db.refresh(new_order)
#
#     # 2️⃣ Add Order Items
#     for item in body.checkouts:
#         subtotal = item.discountPrice * item.quantity
#
#         db_item = OrderItem(
#             order_id=new_order.id,
#             product_id=item.productId,
#             vendor_id=item.vendor,
#             quantity=item.quantity,
#             price=item.price,
#             discount_price=item.discountPrice,
#             type_id=item.type.id,
#             subtotal=subtotal,
#         )
#         db.add(db_item)
#     db.commit()
#
#     # 3️⃣ Initialize Payment (no manual reference)
#     headers = {
#         "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
#         "Content-Type": "application/json",
#     }
#
#     payload = {
#         "email": current_user.email,
#         "amount": int(body.amount * 100),  # Paystack needs amount in kobo
#         # "callback_url":"https://aquasense-backend-jsa5.onrender.com/api/v1/paystack/webhook"
#         # "callback_url": "https://aquasense-backend-jsa5.onrender.com/api/v1/checkout/verify",
#         "callback_url": "https://aquasense-backend-jsa5.onrender.com/api/v1/checkout/paystack/callback"
#     }
#
#     response = requests.post(
#         f"{PAYSTACK_BASE_URL}/transaction/initialize",
#         json=payload,
#         headers=headers,
#     )
#     res_data = response.json()
#
#     if not res_data.get("status"):
#         raise HTTPException(
#             status_code=400,
#             detail=res_data.get("message", "Payment initialization failed"),
#         )
#
#     # 4️⃣ Save Paystack reference in DB
#     paystack_ref = res_data["data"]["reference"]
#     new_order.payment_reference = paystack_ref
#     db.commit()
#
#     # 5️⃣ Return clean response
#     return {
#         "message": "Order created. Proceed to Paystack payment.",
#         "authorization_url": res_data["data"]["authorization_url"],
#         "reference": paystack_ref,
#         "order_id": new_order.id,
#         "user": {
#             "id": current_user.id,
#             "email": current_user.email,
#             "first_name": current_user.first_name,
#             "last_name": current_user.last_name,
#             "profilepicture": getattr(current_user, "profilepicture", None),
#             "phone": getattr(current_user, "phone", None),
#             "kyc_status": getattr(current_user, "kyc_status", "unverified"),
#             "emailverified": getattr(current_user, "emailverified", True),
#         },
#     }
#
#
# # ==============================
# # 🔍 VERIFY PAYMENT
# # ==============================
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
    """
    ✅ Callback URL that Paystack redirects to after payment.
    This verifies the transaction, updates the order, and includes vendor info.
    """
    verify_url = f"{PAYSTACK_BASE_URL}/transaction/verify/{reference}"
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}
    res = requests.get(verify_url, headers=headers)
    data = res.json()

    # 🧾 Find matching order
    order = db.query(Order).filter(Order.payment_reference == reference).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # 📊 Extract key Paystack data
    status = data.get("data", {}).get("status", "failed")
    amount_paid = data.get("data", {}).get("amount", 0) / 100
    channel = data.get("data", {}).get("channel", "unknown")
    gateway_response = data.get("data", {}).get("gateway_response", "")
    currency = data.get("data", {}).get("currency", "NGN")

    # ✅ Update order status
    if status == "success":
        order.status = "paid"
    elif status == "failed":
        order.status = "failed"
    else:
        order.status = "pending"

    db.commit()

    # 🛒 Fetch related items and vendor info
    items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    item_details = []

    for item in items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        vendor = db.query(Vendor).filter(Vendor.id == item.vendor_id).first()

        item_details.append({
            "product": {
                "id": product.id if product else None,
                "name": product.title if product else "Unknown Product",
                "price": item.price,
            },
            "vendor": {
                "id": vendor.id if vendor else None,
                "first_name": vendor.first_name if vendor else None,
                "last_name": vendor.last_name if vendor else None,
                "email": vendor.email if vendor else None,
                "phone": vendor.phone if vendor else None,
                "profilepicture": vendor.profilepicture if vendor else None,
                "pick_up_station_address": vendor.pick_up_station_address if vendor else None,
                "opening_hour":vendor.opening_hour if vendor else None,
            },
            "quantity": item.quantity,
            "subtotal": item.subtotal,
        })

    # 📦 Delivery details (if present)
    delivery = order.delivery_address
    delivery_info = None
    if delivery:
        delivery_info = {
            "recipient_name": delivery.recipient_name,
            "phone_number": delivery.phone_number,
            "address": delivery.address,
            "city": delivery.city,
            "state": delivery.state,
            "postal_code": delivery.postal_code,
            "delivery_instructions": delivery.delivery_instructions,
        }

    # ✅ Prepare full JSON response
    response_data = {
        "success": True,
        "message": "Payment verification completed",
        "payment_status": status,
        "order": {
            "id": order.id,
            "total_amount": order.total_amount,
            "status": order.status,
            "payment_reference": order.payment_reference,
            "delivery_address": delivery_info,
            "items": item_details,
        },
        "paystack": {
            "amount_paid": amount_paid,
            "channel": channel,
            "currency": currency,
            "gateway_response": gateway_response,
        },
    }

    # 🖥️ HTML Response (for browser callback)
    accept_header = request.headers.get("accept", "")
    if "text/html" in accept_header:
        vendor_names = ", ".join([
            f"{i['vendor']['first_name']} {i['vendor']['last_name']}".strip()
            for i in item_details if i["vendor"]["first_name"]
        ]) or "Unknown Vendor"

        html = f"""
        <html>
          <head><title>Payment {status.title()}</title></head>
          <body style="text-align:center; font-family: Arial; margin-top:50px;">
            <h2>Payment Status:
                <span style="color:{'green' if status == 'success' else 'red'}">
                    {status.upper()}
                </span>
            </h2>
            <p><b>Reference:</b> {reference}</p>
            <p><b>Amount Paid:</b> ₦{amount_paid:,.2f}</p>
            <p><b>Payment Method:</b> {channel}</p>
            <p><b>Vendors:</b> {vendor_names}</p>
            <p><b>Gateway Response:</b> {gateway_response}</p>
            <hr>
            {"<p><b>Delivery:</b> " + delivery_info['address'] + ", " + delivery_info['city'] + "</p>" if delivery_info else ""}
            <p>Thank you for shopping with us!</p>
          </body>
        </html>
        """
        return HTMLResponse(content=html)

    # 🧾 JSON for API clients
    return JSONResponse(content=response_data)




# @router.get("/paystack/callback")
# def paystack_callback(reference: str, request: Request, db: Session = Depends(get_db)):
#     """
#     ✅ Callback URL that Paystack redirects to after payment.
#     This verifies the transaction and updates the order status.
#     """
#     verify_url = f"{PAYSTACK_BASE_URL}/transaction/verify/{reference}"
#     headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}
#     res = requests.get(verify_url, headers=headers)
#     data = res.json()
#
#     # Find matching order
#     order = db.query(Order).filter(Order.payment_reference == reference).first()
#     if not order:
#         raise HTTPException(status_code=404, detail="Order not found")
#
#     # Extract key Paystack data
#     status = data.get("data", {}).get("status", "failed")
#     amount_paid = data.get("data", {}).get("amount", 0) / 100
#     channel = data.get("data", {}).get("channel", "unknown")
#     gateway_response = data.get("data", {}).get("gateway_response", "")
#     currency = data.get("data", {}).get("currency", "NGN")
#
#     # ✅ Update payment status in your Order table
#     if status == "success":
#         order.status = "paid"
#     elif status == "failed":
#         order.status = "failed"
#     else:
#         order.status = "pending"
#
#     db.commit()
#
#     # ✅ Prepare response data
#     response_data = {
#         "success": True,
#         "message": "Payment verification completed",
#         "payment_status": status,
#         "order": {
#             "id": order.id,
#             "total_amount": order.total_amount,
#             "status": order.status,
#             "payment_reference": order.payment_reference,
#         },
#         "paystack": {
#             "amount_paid": amount_paid,
#             "channel": channel,
#             "currency": currency,
#             "gateway_response": gateway_response,
#         }
#     }
#
#     # ✅ Detect client type (browser vs API client)
#     accept_header = request.headers.get("accept", "")
#
#     if "text/html" in accept_header:
#         # Return HTML page (for browser redirect)
#         html = f"""
#         <html>
#           <head><title>Payment {status.title()}</title></head>
#           <body style="text-align:center; font-family: Arial; margin-top:50px;">
#             <h2>Payment Status:
#                 <span style="color:{'green' if status == 'success' else 'red'}">
#                     {status.upper()}
#                 </span>
#             </h2>
#             <p>Reference: <b>{reference}</b></p>
#             <p>Amount Paid: ₦{amount_paid:,.2f}</p>
#             <p>Payment Method: {channel}</p>
#             <p>Gateway Response: {gateway_response}</p>
#             <br>
#             <p>Thank you for shopping with us!</p>
#           </body>
#         </html>
#         """
#         return HTMLResponse(content=html)
#
#     # Return JSON for API clients
#     return JSONResponse(content=response_data)
#
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


@router.get("/my-orders", summary="Get all orders for the logged-in user")
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Fetch all orders made by the currently authenticated user,
    including their order items and delivery details.
    """
    user_id = current_user.id

    orders = (
        db.query(Order)
        .filter(Order.user_id == user_id)
        .order_by(Order.id.desc())
        .all()
    )

    if not orders:
        raise HTTPException(status_code=404, detail="No orders found for this user")

    all_orders = []

    for order in orders:
        # 🛒 Fetch items for this order
        items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()

        order_items = []
        for item in items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            vendor = db.query(Vendor).filter(Vendor.id == item.vendor_id).first()

            order_items.append({
                "product": {
                    "id": product.id if product else None,
                    "name": product.title if product else "Unknown Product",
                },
                "vendor": {
                    "id": vendor.id if vendor else None,
                    "name": f"{vendor.first_name or ''} {vendor.last_name or ''}".strip() if vendor else "Unknown Vendor",
                },
                "quantity": item.quantity,
                "price": item.price,
                "discount_price": item.discount_price,
                "subtotal": item.subtotal,
            })

        # 📦 Include delivery address info
        delivery = order.delivery_address
        delivery_info = None
        if delivery:
            delivery_info = {
                "id": delivery.id,
                "recipient_name": delivery.recipient_name,
                "phone_number": delivery.phone_number,
                "address": delivery.address,
                "city": delivery.city,
                "state": delivery.state,
                "postal_code": delivery.postal_code,
                "delivery_instructions": delivery.delivery_instructions,
                "created_at": delivery.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }

        # 🧾 Assemble full order data
        order_data = {
            "id": order.id,
            "total_amount": order.total_amount,
            "status": order.status,
            "reference": order.payment_reference,
            "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "delivery_address": delivery_info,
            "items": order_items,
        }

        all_orders.append(order_data)

    return {
        "success": True,
        "message": "User orders retrieved successfully",
        "user": {
            "id": current_user.id,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "email": current_user.email,
        },
        "total_orders": len(all_orders),
        "orders": all_orders,
    }

# @router.get("/my-orders", summary="Get all orders for the logged-in user")
# def get_my_orders(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Fetch all orders made by the currently authenticated user,
#     including their order items and related details.
#     """
#     user_id = current_user.id
#
#     orders = (
#         db.query(Order)
#         .filter(Order.user_id == user_id)
#         .order_by(Order.id.desc())
#         .all()
#     )
#
#     if not orders:
#         raise HTTPException(status_code=404, detail="No orders found for this user")
#
#     all_orders = []
#
#     for order in orders:
#         # Fetch items for this order
#         items = (
#             db.query(OrderItem)
#             .filter(OrderItem.order_id == order.id)
#             .all()
#         )
#
#         order_items = []
#         for item in items:
#             product = db.query(Product).filter(Product.id == item.product_id).first()
#             vendor = db.query(Vendor).filter(Vendor.id == item.vendor_id).first()
#
#             order_items.append({
#                 "product": {
#                     "id": product.id if product else None,
#                     "name": product.title if product else "Unknown Product",
#                 },
#                 "vendor": {
#                     "id": vendor.id if vendor else None,
#                     "name": f"{vendor.first_name or ''} {vendor.last_name or ''}".strip() if vendor else "Unknown Vendor",
#                 },
#                 "quantity": item.quantity,
#                 "price": item.price,
#                 "discount_price": item.discount_price,
#                 "subtotal": item.subtotal,
#             })
#
#         order_data = {
#             "id": order.id,
#             "total_amount": order.total_amount,
#             "status": order.status,
#             "reference": order.payment_reference,
#             "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
#             "items": order_items,
#         }
#
#         all_orders.append(order_data)
#
#     return {
#         "success": True,
#         "message": "User orders retrieved successfully",
#         "user": {
#             "id": current_user.id,
#             "first_name": current_user.first_name,
#             "last_name": current_user.last_name,
#             "email": current_user.email,
#         },
#         "total_orders": len(all_orders),
#         "orders": all_orders,
#     }
