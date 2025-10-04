from fastapi import APIRouter, Depends, HTTPException, Query
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
    selectspecfictest: str | None = None
    date: str
    username: str   # required


@router.post("/")
def create_lab(lab: LabCreate,   user: User = Depends(get_current_user),db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    new_lab = Labs(
        labtesttorun=lab.labtesttorun,
        selectspecfictest=lab.selectspecfictest,
        date=lab.date,
        username=db_user.name  # captured here
    )
    db.add(new_lab)
    db.commit()
    db.refresh(new_lab)

    return {"message": "Lab test created", "data": new_lab}

@router.get("/")
def get_all_labs(db: Session = Depends(get_db)):
    labs = db.query(Labs).all()
    return {
        "message": "All lab tests retrieved successfully",
        "data": labs
    }