from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy.orm import Session
from passlib.hash import argon2
from uuid import uuid4
from ..database  import get_db
from ..models import User, Farm, Contact, Wait
from ..schemas import UserOut, FarmBase, ContactResponse, ContactCreate, WaitResponse, WaitCreate
from typing import List
# from ..dep.security import create_tokens
from ..dep.security import create_tokens , get_current_user
router = APIRouter(prefix="/waitlist", tags=["waitlist"])



class MainWaitResponse(BaseModel):
    message: str
    waitlist: WaitResponse


class SeeWist(BaseModel):
    message: str
    waitlist:List[WaitResponse]

@router.post("/", response_model=MainWaitResponse)
def create_wait(wait: WaitCreate, db: Session = Depends(get_db)):
    db_wait = Wait(**wait.dict())
    db.add(db_wait)
    db.commit()
    db.refresh(db_wait)
    #
    return {
        "message": "wait list  created",
        "waitlist":  db_wait
    }


@router.get("/", response_model=SeeWist)
def get_all_waitlist(db: Session = Depends(get_db)):
    waitlist =  db.query(Wait).all()
    return {
        "message": "All waitlist ",
        "waitlist": waitlist
    }