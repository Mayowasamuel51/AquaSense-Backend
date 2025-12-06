from fastapi import APIRouter,  Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional, Any
from sqlalchemy.orm import Session
from passlib.hash import argon2
from uuid import uuid4
from ..database  import get_db
from ..models import User, Location
from ..schemas import UserOut
# ,UserProfileUpdate , UserProfileResponse)
from typing import List

from ..dep.security import create_tokens , get_current_user
router = APIRouter(prefix="/profileupdate", tags=["profileupdate"])

class LocationUpdate(BaseModel):
    address: Optional[str] = None
    longitude: Optional[str] = None
    latitude: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    area: Optional[str] = None


class ProfileUpdate(BaseModel):
    nin: Optional[str] = None
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    coins: Optional[int] = None
    location: Optional[LocationUpdate] = None
# Output schema
class LocationOut(LocationUpdate):
    id: int
    class Config:
        from_attributes = True  # allows using ORM objects

class ProfileOut(ProfileUpdate):
    id: int
    location: Optional[LocationOut] = None
    class Config:
        from_attributes = True

class MainResponse(BaseModel):
    message: str
    data: ProfileOut

@router.post("/", response_model=MainResponse)
def profileUpdate(
    body: ProfileUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_user = db.query(User).filter(User.id == user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # --- update user fields ---
    if body.nin is not None:
        db_user.nin = body.nin

    if body.phone is not None:
        db_user.phone = body.phone
        db_user.phone_verified = False  # reset if phone changes

    if body.first_name is not None:
        db_user.first_name = body.first_name

    if body.last_name is not None:
        db_user.last_name = body.last_name

    if body.coins is not None:
        db_user.coins = body.coins

    # --- update or create location ---
    if body.location:
        if db_user.location:  # already exists
            for key, value in body.location.dict(exclude_unset=True).items():
                setattr(db_user.location, key, value)
        else:  # create new
            new_location = Location(
                **body.location.dict(exclude_unset=True),
                user_id=db_user.id
            )
            db.add(new_location)

    db.commit()
    db.refresh(db_user)

    return {"message": "Profile updated successfully", "data": db_user}






# @router.get("/", response_model=UserProfileResponse)
# def get_user_information(
#     user: User = Depends(get_current_user),
#     db: Session = Depends(get_db),
# ):
#     db_user = db.query(User).filter(User.id == user.id).first()
#     if not db_user:
#         raise HTTPException(status_code=404, detail="User not found")
#
#     return {
#         "message": "Showing user information",
#         "data": db_user
#     }
#
#
#
