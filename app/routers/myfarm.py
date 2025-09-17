from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy.orm import Session
from passlib.hash import argon2
from uuid import uuid4
from ..database  import get_db
from ..models import User ,     Farm
from ..schemas import UserOut ,  FarmBase
from typing import List
# from ..dep.security import create_tokens
from ..dep.security import create_tokens , get_current_user
router = APIRouter(prefix="/createfarm", tags=["createfarm"])



class FarmBase(BaseModel):
    address: str | None = None
    longitude: str | None = None
    latitude: str | None = None
    city: str | None = None
    state: str | None = None
    farmname: str | None = None
    farmtype :str| None = None
    area: str | None = None


class FarmOut(BaseModel):
    id: int
    farmname: str
    farmtype: str
    owner_id: int

    class Config:
        from_attributes = True

class FarmResponse(BaseModel):
    message: str
    farm: FarmOut
    user: UserOut


@router.post("/", response_model=FarmResponse)
def create_or_update_farm(
    body: FarmBase,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.id == user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    # Check if the user already has a farm
    existing_farm = db.query(Farm).filter(Farm.owner_id == user.id).first()
    if existing_farm:
        # ✅ Update existing farm
        existing_farm.address = body.address
        existing_farm.longitude = body.longitude
        existing_farm.latitude = body.latitude
        existing_farm.city = body.city
        existing_farm.state = body.state
        existing_farm.farmname = body.farmname
        existing_farm.area = body.area
        existing_farm.farmtype = body.farmtype

        db.commit()
        db.refresh(existing_farm)

        return {
            "message": "You have created your farm successfully",
            "farm": existing_farm,
            "user": db_user
        }
        # return {
        #     "message": "Your farm has been updated successfully",
        #     "id": existing_farm.id,
        #     "farmname": existing_farm.farmname,
        #     "user":db_user,
        #     "farmtpye": existing_farm.farmtype,
        #     "owner_id": existing_farm.owner_id
        # }
    else:
        # ✅ Create new farm
        new_farm = Farm(
            address=body.address,
            longitude=body.longitude,
            latitude=body.latitude,
            city=body.city,
            state=body.state,
            farmname=body.farmname,
            farmtype= body.farmtype,
            area=body.area,
            owner_id=user.id
        )
        db.add(new_farm)
        db.commit()
        db.refresh(new_farm)


        return {
            "message": "You have created your farm successfully",
            "farm": new_farm,
            "user": db_user
        }




# @router.get('/')
# def getfarm(user: User = Depends(get_current_user),  db: Session = Depends(get_db)):
#


# @router.get('/', response_model=List[ShowmyFarm])
# def showmyfarm(user: User = Depends(get_current_user),  db: Session = Depends(get_db)):
#     users = db.query(MyFarm).all()
#     return users


