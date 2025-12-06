from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import hmac
import hashlib
import  os
from ..database import get_db
from ..models import Labs, Order  # ✅ import both models
from ..config import settings

router = APIRouter(prefix="/paystack", tags=["Paystack Webhook"])

# PAYSTACK_SECRET_KEY = settings.PAYSTACK_SECRET_KEY

PAYSTACK_SECRET_KEY = os.getenv(
    "PAYSTACK_SECRET_KEY",
    "sk_test_3e95cf7e607da264fecc599fe380ac04e217944c"
)
PAYSTACK_BASE_URL = os.getenv("PAYSTACK_BASE_URL", "https://api.paystack.co")
@router.post("/webhook")
async def paystack_webhook(request: Request, db: Session = Depends(get_db)):
    """Unified webhook handler for Labs + Product orders"""
    try:
        # 1️⃣ Raw body and signature verification
        body = await request.body()
        signature = request.headers.get("x-paystack-signature")

        if not signature:
            raise HTTPException(status_code=400, detail="Missing Paystack signature")

        computed_signature = hmac.new(
            PAYSTACK_SECRET_KEY.encode(),
            body,
            hashlib.sha512
        ).hexdigest()

        if computed_signature != signature:
            raise HTTPException(status_code=403, detail="Invalid Paystack signature")

        # 2️⃣ Parse payload
        payload = await request.json()
        event = payload.get("event")
        data = payload.get("data", {})
        reference = data.get("reference")
        status = data.get("status")

        print(f"📦 Received Paystack Event: {event} | Ref: {reference}")

        # 3️⃣ Handle payment success/failure
        if event == "charge.success" and status == "success":
            if not reference:
                raise HTTPException(status_code=400, detail="Missing transaction reference")

            # 🧪 Check for Lab Order
            lab = db.query(Labs).filter(Labs.transaction_reference == reference).first()
            if lab:
                lab.payment_status = "success"
                lab.updated_at = datetime.utcnow()
                db.commit()
                print("✅ Lab payment updated successfully")
                return {"status": True, "message": "Lab payment successful and updated"}

            # 🛒 Check for Product Order
            order = db.query(Order).filter(Order.payment_reference == reference).first()
            if order:
                order.status = "paid"
                db.commit()
                print("✅ Product order marked as paid")
                return {"status": True, "message": "Product order payment successful"}

            # ❌ If no match
            print(f"⚠️ No matching order found for reference: {reference}")
            return {"status": False, "message": "No order found for this reference"}

        elif event == "charge.failed":
            # Handle failed payments (both lab and product)
            lab = db.query(Labs).filter(Labs.transaction_reference == reference).first()
            order = db.query(Order).filter(Order.payment_reference == reference).first()

            if lab:
                lab.payment_status = "failed"
                db.commit()
                return {"status": True, "message": "Lab payment marked as failed"}

            if order:
                order.status = "failed"
                db.commit()
                return {"status": True, "message": "Product payment marked as failed"}

            return {"status": False, "message": "No order found for failed payment"}

        # 4️⃣ Default handler for other events
        print(f"Unhandled event: {event}")
        return {"status": True, "message": f"Event '{event}' received but not handled"}

    except Exception as e:
        print("❌ Webhook error:", e)
        return {"status": False, "message": str(e)}
