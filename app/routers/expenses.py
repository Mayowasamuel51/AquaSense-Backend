# from datetime import datetime
# from fastapi import APIRouter, Depends, HTTPException
# from pydantic import BaseModel, EmailStr
# from sqlalchemy.orm import Session
# from passlib.hash import argon2
# from uuid import uuid4
# from ..schemas import UserLearning
# from typing import List
# from ..database  import get_db
# from ..models import User , Learn , IncomeFarm
# from ..dep.security import create_tokens , get_current_user
#
# router = APIRouter(
#     prefix="/expenses",
#      tags=["expenses"],)
#
#
# class Income(BaseModel):
#     email: EmailStr | None = None
#     income_type: str
#     amountearn: int
#     quantity_sold: int
#     total_fish_cost: int
#     which_pond: str
#     income_date: datetime  # ✅ parse automatically
#     payment_method: str
#
# @router.post("/")
# def expenses(body:Income,user: User = Depends(get_current_user),   db: Session = Depends(get_db)):
#     db_user = db.query(User).filter(User.id == user.id).first()
#     mainincome = IncomeFarm(
#         user_id=user.id,
#         income_date=body.income_date,
#         total_fish_cost=body.total_fish_cost,
#         which_pond=body.which_pond,
#         quantity_sold=body.quantity_sold,
#         amountearn=body.amountearn,
#         income_type=body.income_type,
#         payment_method=body.payment_method  # ✅ added
#     )
#     db.add(mainincome)
#     db.commit()
#     db.refresh(mainincome)
#     return {
#         "message": "Your expenses  data saved successfully",
#         "id": mainincome.id,
#         # "user": user.id,   #
#     }
#
#
#
#
