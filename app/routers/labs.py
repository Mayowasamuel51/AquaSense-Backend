# import os
# import requests
# import hmac
# import hashlib
# from datetime import datetime, timedelta
# from fastapi import APIRouter, Depends, HTTPException, Request
# from sqlalchemy.orm import Session
# from ..database import get_db
# from ..models import User, Labs, LabTest
# from ..schemas import UserOut
# from ..dep.security import get_current_user
# router = APIRouter(prefix="/labs", tags=["labs"])
# PAYSTACK_SECRET_KEY = os.getenv(
#     "PAYSTACK_SECRET_KEY",
#     "sk_test_3e95cf7e607da264fecc599fe380ac04e217944c"
# )
# PAYSTACK_BASE_URL = "https://api.paystack.co"
#
#
# # ------------------------------------------------
# # 🔧 Helper: Initialize Paystack
# # ------------------------------------------------
# def initialize_bank_transfer(email: str, amount: float):
#     url = f"{PAYSTACK_BASE_URL}/charge"
#     headers = {
#         "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
#         "Content-Type": "application/json",
#     }
#     # Expire the account after 30 minutes
#     expires_at = (datetime.utcnow() + timedelta(minutes=30)).isoformat() + "Z"
#
#     payload = {
#         "email": email,
#         "amount": int(amount * 100),  # Convert to Kobo
#         "currency": "NGN",
#         "bank_transfer": {
#             "create": True,  # ✅ tells Paystack to create a dedicated transfer account
#             "account_expires_at": expires_at
#         }
#     }
#
#     res = requests.post(url, json=payload, headers=headers)
#
#     try:
#         data = res.json()
#     except Exception:
#         raise HTTPException(status_code=502, detail=f"Invalid Paystack response: {res.text[:200]}")
#
#     print("🔍 Paystack /charge response:", data)
#
#     if not data.get("status"):
#         raise HTTPException(status_code=400, detail=data.get("message", "Paystack bank transfer init failed"))
#
#     return data["data"]
#
# # ------------------------------------------------
# # 🧾 Create Lab Order (Bank Transfer or Card)
# # ------------------------------------------------
# @router.post("/")
# def create_lab_order(
#     payload: dict,
#     db: Session = Depends(get_db),
#     user: User = Depends(get_current_user),
# ):
#     total_price = payload.get("totalPrice", 0)
#     lab_tests = payload.get("labTests", [])
#
#     db_user = db.query(User).filter(User.id == user.id).first()
#     if not db_user:
#         raise HTTPException(status_code=404, detail="User not found")
#     if not lab_tests:
#         raise HTTPException(status_code=400, detail="No lab tests provided")
#
#     # 💾 Create Lab record
#     new_lab = Labs(
#         username=f"{db_user.first_name} {db_user.last_name}",
#         preferred_date=payload.get("preferredDate"),
#         totalPrice=total_price,
#         payment_method="bank_transfer",
#         payment_status="pending",
#         user_id=db_user.id,
#     )
#     db.add(new_lab)
#     db.commit()
#     db.refresh(new_lab)
#
#     # 🧪 Save test items
#     for category in lab_tests:
#         category_title = category.get("title")
#         for test_item in category.get("tests", []):
#             db.add(
#                 LabTest(
#                     lab_id=new_lab.id,
#                     category_title=category_title,
#                     test_id=test_item.get("id") or 0,
#                     test_name=test_item.get("name"),
#                     test_price=test_item.get("price", 0.0),
#                 )
#             )
#     db.commit()
#
#     # 💳 Initialize Paystack bank transfer
#     paystack_data = initialize_bank_transfer(db_user.email, total_price)
#     reference = paystack_data["reference"]
#
#     # Store reference
#     new_lab.transaction_reference = reference
#     db.commit()
#
#     # ✅ Immediately verify to get account details
#     verify_url = f"{PAYSTACK_BASE_URL}/transaction/verify/{reference}"
#     headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}
#     verify_res = requests.get(verify_url, headers=headers).json()
#
#     print("🔎 Paystack Verify Response:", verify_res)
#
#     bank_info = {}
#     if verify_res.get("data") and verify_res["data"].get("authorization"):
#         # In some cases, account info is here
#         bank_info = verify_res["data"]["authorization"]
#     elif verify_res.get("data") and verify_res["data"].get("bank"):
#         bank_info = verify_res["data"]["bank"]
#
#     response_data = {
#         "message": "Bank Transfer payment initialized.",
#         "lab_id": new_lab.id,
#         "reference": reference,
#         "amount": total_price,
#         "user": UserOut.model_validate(db_user).model_dump(),
#         "bank_details": {
#             "account_name": bank_info.get("account_name", "Pending..."),
#             "account_number": bank_info.get("account_number", "Pending..."),
#             "bank_name": bank_info.get("bank_name", "Pending..."),
#         },
#     }
#
#     return response_data
#
# # ------------------------------------------------
# # ✅ Verify Payment (for “I have paid” button)
# # ------------------------------------------------
# @router.get("/verify/{reference}")
# def verify_lab_payment(reference: str, db: Session = Depends(get_db)):
#     """
#     Called when user clicks 'I have paid'
#     """
#     url = f"{PAYSTACK_BASE_URL}/transaction/verify/{reference}"
#     headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}
#     res = requests.get(url, headers=headers)
#     data = res.json()
#
#     if not data.get("status"):
#         raise HTTPException(status_code=400, detail=data.get("message", "Verification failed"))
#
#     transaction = data.get("data", {})
#     status = transaction.get("status")
#
#     lab = db.query(Labs).filter(Labs.transaction_reference == reference).first()
#     if not lab:
#         raise HTTPException(status_code=404, detail="Lab order not found")
#
#     # ✅ If Paystack confirms success
#     if status == "success":
#         lab.payment_status = "success"
#         db.commit()
#         return {
#             "message": "✅ Payment successful",
#             "lab_order": {
#                 "id": lab.id,
#                 "totalprice": lab.totalprice,
#                 "payment_status": lab.payment_status,
#                 "payment_method": lab.payment_method,
#                 "transaction_reference": lab.transaction_reference,
#             },
#             "paystack_response": transaction,
#         }
#
#     # ⚠️ If payment still pending or awaiting transfer
#     bank_info = {}
#     if transaction.get("status") in ["pending", "pending_bank_transfer"]:
#         bank_info = {
#             "account_name": transaction.get("account_name", "Pending..."),
#             "account_number": transaction.get("account_number", "Pending..."),
#             "bank_name": transaction.get("bank", {}).get("name", "Pending..."),
#         }
#
#     return {
#         "message": f"Payment status: {status}",
#         "status": status,
#         "bank_details": bank_info,
#     }
#
#
#
# # ------------------------------------------------
# # 🕊️ Webhook (Paystack calls this automatically)
# # ------------------------------------------------
#
# @router.post("/paystack/webhook")
# async def paystack_webhook(request: Request, db: Session = Depends(get_db)):
#     """
#     Automatically called by Paystack when payment completes.
#     """
#     body = await request.body()
#     signature = request.headers.get("x-paystack-signature")
#
#     # ✅ Verify Paystack signature
#     expected_signature = hmac.new(
#         PAYSTACK_SECRET_KEY.encode(),
#         body,
#         hashlib.sha512
#     ).hexdigest()
#
#     if signature != expected_signature:
#         raise HTTPException(status_code=403, detail="Invalid Paystack signature")
#
#     event = await request.json()
#     data = event.get("data", {})
#     reference = data.get("reference")
#     status = data.get("status")
#
#     print("🔔 Paystack Webhook Received:", event)
#
#     # Update your lab order
#     lab = db.query(Labs).filter(Labs.transaction_reference == reference).first()
#     if not lab:
#         return {"status": "ignored", "message": "Reference not found"}
#
#     if status == "success":
#         lab.payment_status = "success"
#         db.commit()
#         print(f"✅ Payment confirmed for lab ID {lab.id}")
#
#     return {"status": "ok"}



from fastapi.templating import Jinja2Templates
import os
import hmac
import hashlib
import requests
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException , Request
from sqlalchemy.orm import Session
from uuid import uuid4
from typing import List, Optional
from pydantic import BaseModel
from starlette.responses import HTMLResponse

from ..database import get_db
from ..models import User, Labs, LabTest
from ..dep.security import get_current_user
from ..schemas import UserOut
router = APIRouter(prefix="/labs", tags=["labs"])

# templates folder (create this folder at project root or app directory)
templates = Jinja2Templates(directory="templates")
# Paystack environment setup
PAYSTACK_SECRET_KEY = os.getenv(
    "PAYSTACK_SECRET_KEY", "sk_test_3e95cf7e607da264fecc599fe380ac04e217944c"
)
PAYSTACK_BASE_URL = os.getenv("PAYSTACK_BASE_URL", "https://api.paystack.co")

# -------------------------------
# ✅ Paystack helper
# -------------------------------
def initialize_paystack(email: str, amount: float):
    """Initialize Paystack transaction (Naira → Kobo)"""
    url = f"{PAYSTACK_BASE_URL}/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "email": email,
        "amount": int(amount * 100),
        "callback_url":"https://aquasense-backend-jsa5.onrender.com/api/v1/labs/paystack/callback"
    }

    res = requests.post(url, json=payload, headers=headers)
    if res.status_code != 200:
        raise HTTPException(status_code=400, detail="Paystack initialization failed")

    return res.json()["data"]


# -------------------------------
# ✅ Schemas for request payload
# -------------------------------
class TestItem(BaseModel):
    id: int
    name: str
    price: float

class LabTestCategory(BaseModel):
    title: str
    tests: List[TestItem]

class LabCreate(BaseModel):
    userId: Optional[str] = None
    preferredDate: str
    labTests: List[LabTestCategory]
    totalPrice: float

# -------------------------------
# ✅ Create new lab order
# -------------------------------
@router.post("/")
def create_lab_order(
    payload: LabCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    db_user = db.query(User).filter(User.id == user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # 💾 Create Lab record
    new_lab = Labs(
        username=f"{db_user.first_name} {db_user.last_name}",
        preferred_date=payload.preferredDate,
        totalPrice=payload.totalPrice,
        payment_method="paystack",
        payment_status="pending",
        user_id=db_user.id
    )
    db.add(new_lab)
    db.commit()
    db.refresh(new_lab)

    # 🧪 Save all test categories + tests
    for category in payload.labTests:
        for test_item in category.tests:
            db.add(
                LabTest(
                    lab_id=new_lab.id,
                    category_title=category.title,
                    test_id=test_item.id,
                    test_name=test_item.name,
                    test_price=test_item.price,
                )
            )
    db.commit()

    # 💳 Initialize Paystack payment
    try:
        paystack_data = initialize_paystack(db_user.email, payload.totalPrice)
        authorization_url = paystack_data["authorization_url"]
        reference = paystack_data["reference"]

        user_out = UserOut.from_orm(db_user)
        # Save the transaction reference
        new_lab.transaction_reference = reference
        db.commit()

        return {
            "message": "Lab order created. Proceed to Paystack payment.",
            "authorization_url": authorization_url,
            "reference": reference,
            "lab_id": new_lab.id,
            "user":user_out
        }

    except Exception as e:
        db.delete(new_lab)
        db.commit()
        raise HTTPException(status_code=400, detail=f"Paystack initialization failed: {str(e)}")


# -------------------------------
# ✅ Verify Paystack Payment
# -------------------------------
@router.get("/verify/{reference}")
def verify_lab_payment(reference: str, db: Session = Depends(get_db)):
    url = f"{PAYSTACK_BASE_URL}/transaction/verify/{reference}"
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}
    res = requests.get(url, headers=headers)
    data = res.json()

    lab = db.query(Labs).filter(Labs.transaction_reference == reference).first()
    if not lab:
        raise HTTPException(status_code=404, detail="Lab order not found")

    if data.get("status") and data["data"]["status"] == "success":
        lab.payment_status = "success"
        db.commit()

        user = db.query(User).filter(User.id == lab.user_id).first()
        paid_amount = data["data"]["amount"] / 100  # Kobo → Naira

        return {
            "message": "Payment successful",
            "lab_order": {
                "id": lab.id,
                "totalPrice": lab.totalPrice,
                "payment_status": lab.payment_status,
                "payment_method": lab.payment_method,
                "transaction_reference": lab.transaction_reference,
            },
            "user": {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
            },
            "paystack": {
                "paid_amount": paid_amount,
                "gateway_response": data["data"]["gateway_response"],
                "channel": data["data"]["channel"],
                "currency": data["data"]["currency"],
            },
        }

    return {"message": "Payment failed", "data": data}

@router.post("/paystack/webhook")
async def paystack_webhook(request: Request, db: Session = Depends(get_db)):
    """Secure Paystack webhook endpoint"""
    try:
        # 1️⃣ Get raw body (used for signature verification)
        body = await request.body()
        signature = request.headers.get("x-paystack-signature")

        if not signature:
            raise HTTPException(status_code=400, detail="Missing Paystack signature")

        # 2️⃣ Compute signature to verify authenticity
        computed_signature = hmac.new(
            PAYSTACK_SECRET_KEY.encode(),
            body,
            hashlib.sha512
        ).hexdigest()

        if computed_signature != signature:
            raise HTTPException(status_code=403, detail="Invalid Paystack signature")

        # 3️⃣ Parse JSON payload
        payload = await request.json()
        event = payload.get("event")
        data = payload.get("data", {})

        reference = data.get("reference")
        amount_paid = data.get("amount", 0) / 100  # kobo → naira
        status = data.get("status")

        # 4️⃣ Find matching lab order
        lab = db.query(Labs).filter(Labs.transaction_reference == reference).first()
        if not lab:
            raise HTTPException(status_code=404, detail="Lab order not found")

        # 5️⃣ Handle Paystack events
        if event == "charge.success" and status == "success":
            lab.payment_status = "success"
            db.commit()
            return {"status": True, "message": "Payment successful and updated"}

        elif event == "charge.failed":
            lab.payment_status = "failed"
            db.commit()
            return {"status": True, "message": "Payment failed and updated"}

        # 6️⃣ Handle other events gracefully
        return {"status": True, "message": f"Event '{event}' received but not handled"}

    except Exception as e:
        print("Webhook error:", e)
        return {"status": False, "message": str(e)}


router.get("/paystack/callback", response_class=HTMLResponse)
def paystack_callback(request: Request, reference: str, db: Session = Depends(get_db)):
    """
    Callback URL Paystack redirects to after payment:
    GET /api/v1/labs/paystack/callback?reference=<reference>
    This verifies the reference with Paystack and renders an HTML result page.
    """
    # Verify with Paystack
    url = f"{PAYSTACK_BASE_URL}/transaction/verify/{reference}"
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        data = res.json()
    except Exception as e:
        # Render an error template with the exception message
        context = {
            "request": request,
            "status": "error",
            "title": "Verification Error",
            "message": f"Failed to contact Paystack: {str(e)}",
            "reference": reference,
            "lab": None,
            "paystack": None,
        }
        return templates.TemplateResponse("payment_result.html", context)

    # find lab order
    lab = db.query(Labs).filter(Labs.transaction_reference == reference).first()

    if not data.get("status"):
        # Paystack returned an error: show message
        context = {
            "request": request,
            "status": "error",
            "title": "Payment Verification Failed",
            "message": data.get("message", "Unknown error from Paystack"),
            "reference": reference,
            "lab": lab,
            "paystack": data.get("data"),
        }
        return templates.TemplateResponse("payment_result.html", context)

    tx = data.get("data", {})
    tx_status = tx.get("status")

    # Update DB if success
    if lab and tx_status == "success":
        lab.payment_status = "success"
        db.commit()

    # Prepare context data for the template
    context = {
        "request": request,
        "status": "success" if tx_status == "success" else "pending",
        "title": "Payment Result",
        "message": "Payment completed successfully." if tx_status == "success" else f"Payment status: {tx_status}",
        "reference": reference,
        "lab": {
            "id": lab.id,
            "preferred_date": getattr(lab, "preferred_date", None),
            "totalPrice": getattr(lab, "totalPrice", None),
            "payment_status": getattr(lab, "payment_status", None),
        } if lab else None,
        "paystack": {
            "amount": tx.get("amount"),
            "gateway_response": tx.get("gateway_response"),
            "channel": tx.get("channel"),
            "currency": tx.get("currency"),
        },
    }

    return templates.TemplateResponse("payment_result.html", context)
# # @router.post("/")
# # def create_lab_order(
# #     lab: LabCreate,
# #     db: Session = Depends(get_db),
# #     user: User = Depends(get_current_user),
# # ):
# #     db_user = db.query(User).filter(User.id == user.id).first()
# #     if not db_user:
# #         raise HTTPException(status_code=404, detail="User not found")
# #
# #     # -------------------------
# #     # 1️⃣ Coin cap logic
# #     # -------------------------
# #     coins_available = db_user.coins
# #     coin_cap = min(LABS_COIN_CAP, lab.amount)
# #     coins_used = min(coins_available, coin_cap)
# #     cash_needed = lab.amount - coins_used
# #
# #     # -------------------------
# #     # 2️⃣ Deduct coins immediately
# #     # -------------------------
# #     db_user.coins -= coins_used
# #     db.commit()
# #
# #     # -------------------------
# #     # 3️⃣ Create lab order
# #     # -------------------------
# #     new_lab = Labs(
# #         labtesttorun=lab.labtesttorun,
# #         selectspecfictest=lab.selectspecfictest,
# #         date=lab.date,
# #         username=f"{db_user.first_name} {db_user.last_name}",
# #         amount=lab.amount,
# #         coin_used=coins_used,
# #         user_id= db_user.id,
# #         payment_method="coins+paystack" if cash_needed > 0 else "coins",
# #         payment_status="pending" if cash_needed > 0 else "success",
# #     )
# #     db.add(new_lab)
# #     db.commit()
# #     db.refresh(new_lab)
# #
# #     # -------------------------
# #     # 4️⃣ If cash needed → Paystack
# #     # -------------------------
# #     if cash_needed > 0:
# #         paystack_data = initialize_paystack(lab.email, cash_needed, db, user)
# #         new_lab.transaction_reference = paystack_data["reference"]
# #         db.commit()
# #
# #         return {
# #             "message": "Part coins deducted. Continue with Paystack.",
# #             "coins_used": coins_used,
# #             "cash_needed": cash_needed,
# #             "authorization_url": paystack_data["authorization_url"],
# #             "reference": paystack_data["reference"],
# #             "data": {
# #                 "id": db_user.id,
# #                 "first_name": db_user.first_name,
# #                 "last_name": db_user.last_name,
# #                 "email": db_user.email,
# #                 "coins": db_user.coins,
# #             },
# #             "lab_order": {
# #                 "id": new_lab.id,
# #                 "labtesttorun": new_lab.labtesttorun,
# #                 "selectspecfictest": new_lab.selectspecfictest,
# #                 "amount": new_lab.amount,
# #                 "coins_used": new_lab.coin_used,
# #                 "payment_status": new_lab.payment_status,
# #                 "payment_method": new_lab.payment_method,
# #             },
# #         }
# #
# #     # -------------------------
# #     # 5️⃣ Fully paid with coins
# #     # -------------------------
# #     return {
# #         "message": "Lab order paid fully with coins.",
# #         "coins_used": coins_used,
# #         "cash_needed": 0,
# #         "user": {
# #             "id": db_user.id,
# #             "first_name": db_user.first_name,
# #             "last_name": db_user.last_name,
# #             "email": db_user.email,
# #             "coins_remaining": db_user.coins,
# #         },
# #         "lab_order": {
# #             "id": new_lab.id,
# #             "labtesttorun": new_lab.labtesttorun,
# #             "selectspecfictest": new_lab.selectspecfictest,
# #             "amount": new_lab.amount,
# #             "coins_used": new_lab.coin_used,
# #             "payment_status": new_lab.payment_status,
# #             "payment_method": new_lab.payment_method,
# #         },
# #     }
#
#
# # -------------------------------
# # Paystack verification
# # -------------------------------
#
#
#
# #
# # @router.post("/")
# # def create_lab(
# #         lab: LabCreate,
# #         db: Session = Depends(get_db),
# #         user: User = Depends(get_current_user)
# # ):
# #     # Check if user exists
# #     db_user = db.query(User).filter(User.id == user.id).first()
# #     if not db_user:
# #         raise HTTPException(status_code=404, detail="User not found")
# #     LAB_COST = lab.amount  # ✅ use dynamic amount from request
# #
# #     if lab.payment_method == "coins":
# #         if user.coins < LAB_COST:
# #             raise HTTPException(status_code=400, detail="Insufficient coins")
# #
# #         user.coins -= LAB_COST
# #         db.add(user)
# #         db.commit()
# #         db.refresh(user)
# #
# #         new_lab = Labs(
# #             labtesttorun=lab.labtesttorun,
# #             selectspecfictest=lab.selectspecfictest,
# #             date=lab.date,
# #             username=db_user.first_name,
# #             amount=lab.amount
# #         )
# #         db.add(new_lab)
# #         db.commit()
# #         db.refresh(new_lab)
# #
# #         return {
# #             "message": "Lab test created successfully (paid with coins)",
# #             "data": {
# #                 "lab": {
# #                     "id": new_lab.id,
# #                     "labtesttorun": new_lab.labtesttorun,
# #                     "selectspecfictest": new_lab.selectspecfictest,
# #                     "date": new_lab.date,
# #                     "username": new_lab.username,
# #                     "amount": new_lab.amount
# #                 },
# #                 "user": db_user,
# #                 "balance": user.coins
# #             }
# #         }
# #
# #     elif lab.payment_method == "paystack":
# #         amount_kobo = LAB_COST * 100
# #         paystack_payload = {
# #             "email": user.email,
# #             "amount": amount_kobo
# #         }
# #         # 🔔 Call Paystack API in real implementation
# #         return {
# #             "message": "Lab test created successfully (pending Paystack payment)",
# #             "data": {
# #                 "lab": {
# #                     "labtesttorun": lab.labtesttorun,
# #                     "selectspecfictest": lab.selectspecfictest,
# #                     "date": lab.date,
# #                     "username": user.first_name,
# #                     "amount": lab.amount
# #                 },
# #                 "payment": paystack_payload,
# #                 "balance": user.coins
# #             }
# #         }
# #
# #     else:
# #         raise HTTPException(status_code=400, detail="Invalid payment method")
#
#
