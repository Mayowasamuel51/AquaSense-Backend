from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy.orm import Session
from passlib.hash import argon2
from uuid import uuid4
from ..database  import get_db
from ..models import User
from ..schemas import UserOut
from typing import List
# from ..dep.security import create_tokens
from ..dep.security import create_tokens , get_current_user
router = APIRouter(prefix="/profileupdate", tags=["profileupdate"])



class ProfileUpdate(BaseModel):
    nin: str | None = None
    phone: str | None = None
    location: str | None = None
    first_name: str | None = None
    last_name: str | None = None



@router.post('/')
def profileUpdate(body:ProfileUpdate, user: User = Depends(get_current_user),   db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_user = db.query(User).filter(User.id == user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if body.nin is not None:
        db_user.nin = body.nin

    if body.phone is not None:
        db_user.phone = body.phone
        db_user.phone_verified = False  # reset if phone changes

    if body.location is not None:
        db_user.location = body.location

    if body.first_name is not None:
        db_user.first_name = body.first_name

    if body.last_name is not None:
        db_user.last_name = body.last_name

    db.commit()
    db.refresh(db_user)

    return {"message": "Profile updated successfully"}

