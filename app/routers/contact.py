from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy.orm import Session
from passlib.hash import argon2
from uuid import uuid4
from ..database  import get_db
from ..models import User, Farm, Contact
from ..schemas import UserOut, FarmBase, ContactResponse, ContactCreate
from typing import List
# from ..dep.security import create_tokens
from ..dep.security import create_tokens , get_current_user
router = APIRouter(prefix="/contact", tags=["contact"])



class MainContactResponse(BaseModel):
    message: str
    contact: ContactResponse

class SeeContact(BaseModel):
    message: str
    contact:List[ContactResponse]

@router.post("/", response_model=MainContactResponse)
def create_contact(contact: ContactCreate, db: Session = Depends(get_db)):
    db_contact =Contact(**contact.dict())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return {
        "message":"Contact created",
        "contact":db_contact
    }



@router.get("/", response_model=SeeContact)
def get_all_contacts(db: Session = Depends(get_db)):
    contact =  db.query(Contact).all()
    return {
        "message":"All contacts ",
        "contact":contact
    }