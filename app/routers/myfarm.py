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
    area: str | None = None

@router.post('/')
def farm(body: FarmBase, user: User = Depends(get_current_user),   db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    new_farm = Farm(
        address=body.address,
        longitude=body.longitude,
        latitude=body.latitude,
        city=body.city,
        state=body.state,
        farmname=body.farmname,
        area=body.area,
        owner_id=user.id
    )
    db.add(new_farm)
    db.commit()
    db.refresh(new_farm)

    return {
        "message": "You have created your Farm successfully",
        "id": new_farm.id,
        "farmname": new_farm.farmname,
        "owner_id": new_farm.owner_id
    }

# @router.get('/', response_model=List[ShowmyFarm])
# def showmyfarm(user: User = Depends(get_current_user),  db: Session = Depends(get_db)):
#     users = db.query(MyFarm).all()
#     return users


