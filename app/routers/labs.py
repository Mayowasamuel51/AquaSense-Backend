from fastapi import APIRouter, Depends, HTTPException, Query, Body
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

class LabCreate(BaseModel):
    labtesttorun: str
    selectspecfictest: Optional[str] = None
    date: str
    amount: int  # ✅ comes from client
    payment_method: str  # "coins" or "paystack"


@router.post("/")
def create_lab(
        lab: LabCreate,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    # Check if user exists
    db_user = db.query(User).filter(User.id == user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    LAB_COST = lab.amount  # ✅ use dynamic amount from request

    if lab.payment_method == "coins":
        if user.coins < LAB_COST:
            raise HTTPException(status_code=400, detail="Insufficient coins")

        user.coins -= LAB_COST
        db.add(user)
        db.commit()
        db.refresh(user)

        new_lab = Labs(
            labtesttorun=lab.labtesttorun,
            selectspecfictest=lab.selectspecfictest,
            date=lab.date,
            username=db_user.first_name,
            amount=lab.amount
        )
        db.add(new_lab)
        db.commit()
        db.refresh(new_lab)

        return {
            "message": "Lab test created successfully (paid with coins)",
            "data": {

                "lab": {
                    "id": new_lab.id,
                    "labtesttorun": new_lab.labtesttorun,
                    "selectspecfictest": new_lab.selectspecfictest,
                    "date": new_lab.date,
                    "username": new_lab.username,
                    "amount": new_lab.amount
                },
                "user": db_user,
                "balance": user.coins
            }
        }

    elif lab.payment_method == "paystack":
        amount_kobo = LAB_COST * 100
        paystack_payload = {
            "email": user.email,
            "amount": amount_kobo
        }
        # 🔔 Call Paystack API in real implementation
        return {
            "message": "Lab test created successfully (pending Paystack payment)",
            "data": {
                "lab": {
                    "labtesttorun": lab.labtesttorun,
                    "selectspecfictest": lab.selectspecfictest,
                    "date": lab.date,
                    "username": user.first_name,
                    "amount": lab.amount
                },
                "payment": paystack_payload,
                "balance": user.coins
            }
        }

    else:
        raise HTTPException(status_code=400, detail="Invalid payment method")


# @router.post("/")
# def create_lab(lab: LabCreate,   user: User = Depends(get_current_user),db: Session = Depends(get_db)):
#     db_user = db.query(User).filter(User.id == user.id).first()
#     if not db_user:
#         raise HTTPException(status_code=404, detail="User not found")
#     new_lab = Labs(
#         labtesttorun=lab.labtesttorun,
#         selectspecfictest=lab.selectspecfictest,
#         date=lab.date,
#         username=db_user.name  # captured here
#     )
#     db.add(new_lab)
#     db.commit()
#     db.refresh(new_lab)
#
#     return {"message": "Lab test created", "data": new_lab}

# @router.post("/labs/order")
# def create_lab_order(
#     lab: LabCreate,
#     payment_method: str = Body(..., embed=True),  # "coins" or "paystack"
#     db: Session = Depends(get_db),
#     user: User = Depends(get_current_user)  # logged in user
# ):
#     amount = lab.amount  # cost of test
#
#     # ✅ If paying with coins
#     if payment_method == "coins":
#         if user.coins < amount:
#             raise HTTPException(status_code=400, detail="Not enough coins")
#
#         # Deduct coins
#         user.coins -= amount
#         new_lab = Labs(
#             labtesttorun=lab.labtesttorun,
#             selectspecfictest=lab.selectspecfictest,
#             date=lab.date,
#             username=user.first_name,
#             amount=amount,
#             payment_status="paid",
#             payment_method="coins"
#         )
#         db.add(new_lab)
#         db.commit()
#         db.refresh(new_lab)
#         return {"message": "Lab test ordered with coins", "data": new_lab}
#
#     # ✅ If paying with Paystack
#     elif payment_method == "paystack":
#         headers = {
#             "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
#             "Content-Type": "application/json"
#         }
#         payload = {
#             "email": user.email,
#             "amount": amount * 100,  # kobo
#         }
#
#         response = requests.post("https://api.paystack.co/transaction/initialize",
#                                  headers=headers, json=payload)
#         data = response.json()
#
#         if not data["status"]:
#             raise HTTPException(status_code=400, detail="Payment initialization failed")
#
#         new_lab = Labs(
#             labtesttorun=lab.labtesttorun,
#             selectspecfictest=lab.selectspecfictest,
#             date=lab.date,
#             username=user.first_name,
#             amount=amount,
#             payment_status="unpaid",
#             payment_method="paystack",
#             payment_reference=data["data"]["reference"]
#         )
#         db.add(new_lab)
#         db.commit()
#         db.refresh(new_lab)
#
#         return {
#             "message": "Payment initialized",
#             "authorization_url": data["data"]["authorization_url"],
#             "reference": data["data"]["reference"],
#             "lab_order_id": new_lab.id
#         }
#
#     else:
#         raise HTTPException(status_code=400, detail="Invalid payment method")

@router.get("/")
def get_all_labs(db: Session = Depends(get_db)):
    labs = db.query(Labs).all()
    return {
        "message": "All lab tests retrieved successfully",
        "data": labs
    }