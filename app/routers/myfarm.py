from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy.orm import Session
from passlib.hash import argon2
from uuid import uuid4
from ..database  import get_db
from ..models import User ,     MyFarm
from ..schemas import UserOut
from typing import List
# from ..dep.security import create_tokens
from ..dep.security import create_tokens , get_current_user
router = APIRouter(prefix="/createmyfarm", tags=["createmyfarm"])



class MyfarmBase(BaseModel):
    email: EmailStr | None = None
    farm_name:str

@router.post('/')
def farm(body:MyfarmBase, user: User = Depends(get_current_user),   db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    createfarm = MyFarm(
        user_id=user.id,
        farm_name= body.farm_name
    )
    db.add(createfarm)
    db.commit()
    db.refresh(createfarm)
    return {
        "message": "Your have Created your Farm successfully",
        "id": createfarm.id,
        # "user": user.id,   #
    }

