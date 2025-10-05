import os

from fastapi import APIRouter, Depends, HTTPException, Query, Body
import requests  # ✅ real requests library
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy.orm import Session
from passlib.hash import argon2
from uuid import uuid4
from ..database  import get_db
from ..models import User, Product, PriceRange, Cart, ProductType, Labs
from ..schemas import (UserOut, FarmBase, UserCreate, ProductOut)
from typing import List
from ..dep.security import create_tokens , get_current_user
router = APIRouter(prefix="/labs", tags=["labs"])
# class LabCreate(BaseModel):
#     labtesttorun: str
#     selectspecfictest: Optional[str] = None
#     date: str
#     amount: int  # ✅ comes from client
#     payment_method: str  # "coins" or "paystack"
PAYSTACK_SECRET_KEY = os.getenv(
    "PAYSTACK_SECRET_KEY", "sk_test_3e95cf7e607da264fecc599fe380ac04e217944c"
)
PAYSTACK_BASE_URL = os.getenv("PAYSTACK_BASE_URL", "https://api.paystack.co")

LABS_COIN_CAP = 200  # Max coins applicable per lab

# -------------------------------
# Paystack initialization helper
# -------------------------------
def initialize_paystack(email: str, amount: int, db: Session, user: User):
    """Initialize Paystack transaction (amount in Naira -> convert to kobo)"""
    db_user = db.query(User).filter(User.id == user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    url = f"{PAYSTACK_BASE_URL}/transaction/initialize"
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}
    payload = {
        "email": db_user.email,
        "amount": amount * 100,  # Naira → Kobo
    }

    res = requests.post(url, json=payload, headers=headers)
    if res.status_code != 200:
        raise HTTPException(status_code=400, detail="Paystack init failed")

    return res.json()["data"]


# -------------------------------
# Lab order creation
# -------------------------------
class LabCreate(BaseModel):
    labtesttorun: str
    selectspecfictest: Optional[str] = None
    date: str
    amount: int
    username: Optional[str] = None
    email: Optional[str] = None


@router.post("/")
def create_lab_order(
    lab: LabCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    db_user = db.query(User).filter(User.id == user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # -------------------------
    # 1️⃣ Coin cap logic
    # -------------------------
    coins_available = db_user.coins
    coin_cap = min(LABS_COIN_CAP, lab.amount)
    coins_used = min(coins_available, coin_cap)
    cash_needed = lab.amount - coins_used

    # -------------------------
    # 2️⃣ Deduct coins immediately
    # -------------------------
    db_user.coins -= coins_used
    db.commit()

    # -------------------------
    # 3️⃣ Create lab order
    # -------------------------
    new_lab = Labs(
        labtesttorun=lab.labtesttorun,
        selectspecfictest=lab.selectspecfictest,
        date=lab.date,
        username=f"{db_user.first_name} {db_user.last_name}",
        amount=lab.amount,
        coin_used=coins_used,
        user_id= db_user.id,
        payment_method="coins+paystack" if cash_needed > 0 else "coins",
        payment_status="pending" if cash_needed > 0 else "success",
    )
    db.add(new_lab)
    db.commit()
    db.refresh(new_lab)

    # -------------------------
    # 4️⃣ If cash needed → Paystack
    # -------------------------
    if cash_needed > 0:
        paystack_data = initialize_paystack(lab.email, cash_needed, db, user)
        new_lab.transaction_reference = paystack_data["reference"]
        db.commit()

        return {
            "message": "Part coins deducted. Continue with Paystack.",
            "coins_used": coins_used,
            "cash_needed": cash_needed,
            "authorization_url": paystack_data["authorization_url"],
            "reference": paystack_data["reference"],
            "data": {
                "id": db_user.id,
                "first_name": db_user.first_name,
                "last_name": db_user.last_name,
                "email": db_user.email,
                "coins": db_user.coins,
            },
            "lab_order": {
                "id": new_lab.id,
                "labtesttorun": new_lab.labtesttorun,
                "selectspecfictest": new_lab.selectspecfictest,
                "amount": new_lab.amount,
                "coins_used": new_lab.coin_used,
                "payment_status": new_lab.payment_status,
                "payment_method": new_lab.payment_method,
            },
        }

    # -------------------------
    # 5️⃣ Fully paid with coins
    # -------------------------
    return {
        "message": "Lab order paid fully with coins.",
        "coins_used": coins_used,
        "cash_needed": 0,
        "user": {
            "id": db_user.id,
            "first_name": db_user.first_name,
            "last_name": db_user.last_name,
            "email": db_user.email,
            "coins_remaining": db_user.coins,
        },
        "lab_order": {
            "id": new_lab.id,
            "labtesttorun": new_lab.labtesttorun,
            "selectspecfictest": new_lab.selectspecfictest,
            "amount": new_lab.amount,
            "coins_used": new_lab.coin_used,
            "payment_status": new_lab.payment_status,
            "payment_method": new_lab.payment_method,
        },
    }


# -------------------------------
# Paystack verification
# -------------------------------
@router.get("/labs/paystack/verify/{reference}")
def verify_lab_payment(reference: str, db: Session = Depends(get_db)):
    url = f"{PAYSTACK_BASE_URL}/transaction/verify/{reference}"
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}
    res = requests.get(url, headers=headers)
    data = res.json()
    lab = db.query(Labs).filter(Labs.transaction_reference == reference).first()
    if not lab:
        raise HTTPException(404, "Lab order not found")

    if data["status"] and data["data"]["status"] == "success":
        lab.payment_status = "success"
        db.commit()

        # Convert kobo → Naira for frontend
        paid_naira = data["data"]["amount"] / 100
        requested_naira = data["data"]["requested_amount"] / 100

        user = db.query(User).filter(User.id == lab.user_id).first()

        return {
            "message": "Payment successful",
            "lab_order": {
                "id": lab.id,
                "labtesttorun": lab.labtesttorun,
                "selectspecfictest": lab.selectspecfictest,
                "amount": lab.amount,
                "coins_used": lab.coin_used,
                "payment_status": lab.payment_status,
                "payment_method": lab.payment_method,
                "transaction_reference": lab.transaction_reference,
            },
            "user": {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "coins_remaining": user.coins,
            },
            "paystack_payment": {
                "paid_amount_naira": paid_naira,
                "requested_amount_naira": requested_naira,
                "gateway_response": data["data"]["gateway_response"],
                "channel": data["data"]["channel"],
                "currency": data["data"]["currency"],
            },
        }

    return {"message": "Payment failed", "data": data}


#
# @router.post("/")
# def create_lab(
#         lab: LabCreate,
#         db: Session = Depends(get_db),
#         user: User = Depends(get_current_user)
# ):
#     # Check if user exists
#     db_user = db.query(User).filter(User.id == user.id).first()
#     if not db_user:
#         raise HTTPException(status_code=404, detail="User not found")
#     LAB_COST = lab.amount  # ✅ use dynamic amount from request
#
#     if lab.payment_method == "coins":
#         if user.coins < LAB_COST:
#             raise HTTPException(status_code=400, detail="Insufficient coins")
#
#         user.coins -= LAB_COST
#         db.add(user)
#         db.commit()
#         db.refresh(user)
#
#         new_lab = Labs(
#             labtesttorun=lab.labtesttorun,
#             selectspecfictest=lab.selectspecfictest,
#             date=lab.date,
#             username=db_user.first_name,
#             amount=lab.amount
#         )
#         db.add(new_lab)
#         db.commit()
#         db.refresh(new_lab)
#
#         return {
#             "message": "Lab test created successfully (paid with coins)",
#             "data": {
#                 "lab": {
#                     "id": new_lab.id,
#                     "labtesttorun": new_lab.labtesttorun,
#                     "selectspecfictest": new_lab.selectspecfictest,
#                     "date": new_lab.date,
#                     "username": new_lab.username,
#                     "amount": new_lab.amount
#                 },
#                 "user": db_user,
#                 "balance": user.coins
#             }
#         }
#
#     elif lab.payment_method == "paystack":
#         amount_kobo = LAB_COST * 100
#         paystack_payload = {
#             "email": user.email,
#             "amount": amount_kobo
#         }
#         # 🔔 Call Paystack API in real implementation
#         return {
#             "message": "Lab test created successfully (pending Paystack payment)",
#             "data": {
#                 "lab": {
#                     "labtesttorun": lab.labtesttorun,
#                     "selectspecfictest": lab.selectspecfictest,
#                     "date": lab.date,
#                     "username": user.first_name,
#                     "amount": lab.amount
#                 },
#                 "payment": paystack_payload,
#                 "balance": user.coins
#             }
#         }
#
#     else:
#         raise HTTPException(status_code=400, detail="Invalid payment method")


