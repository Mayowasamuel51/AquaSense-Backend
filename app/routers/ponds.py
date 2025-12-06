# from datetime import datetime
# from fastapi import APIRouter, Depends, HTTPException
# from pydantic import BaseModel, EmailStr
# from sqlalchemy.orm import Session
# from passlib.hash import argon2
# from uuid import uuid4
# from ..schemas import UserLearning, PondCreate
# from typing import List
# from ..database  import get_db
# from ..models import User , Learn , IncomeFarm, Pond
# from ..dep.security import create_tokens , get_current_user
#
# router = APIRouter(
#     prefix="/ponds",
#      tags=["ponds"],)
#
# #  user will create each ponds , and the ponds will be under the farm name , and also will need to have data , and guess for them
# # user can update there ponds anytime , and user can move ponds ino
#
#
# router.post('/')
# def create_pond(body:PondCreate,user: User = Depends(get_current_user),   db: Session = Depends(get_db)):
#     db_user = db.query(User).filter(User.id == user.id).first()
#     if not db_user:
#         raise HTTPException(status_code=404, detail="User not found")
#     pondinfomation = Pond(
#         user_id=user.id,
#         # user_farm =
#         pond_name = body. pond_name,
#         pond_type=body. pond_type ,
#     pond_capacity = body. pond_capacity,
#     pond_image_path =body.pond_image_path
#     )
#     db.add( pondinfomation)
#     db.commit()
#     db.refresh( pondinfomation)
#     return {
#         "message": "Pond  data saved successfully",
#         "id":  pondinfomation.id,
#         # "user": user.id,   #
#     }
