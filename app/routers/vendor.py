from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.hash import argon2
import jwt
from pydantic import BaseModel, EmailStr
from ..database import get_db
from ..models import Vendor
from ..config import settings
from ..schemas import VendorRegister, VendorResponse

router = APIRouter(prefix="/vendor", tags=["Vendor Authentication"])

SECRET_KEY = settings.JWT_SECRET
ALGORITHM = "HS256"


def create_vendor_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


# ----------- REGISTER VENDOR -----------
class MainoutVendor(BaseModel):
    data:VendorResponse
    message:str


@router.post("/register", response_model=MainoutVendor)
def register_vendor(body: VendorRegister, db: Session = Depends(get_db)):
    existing = db.query(Vendor).filter(Vendor.email == body.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = argon2.hash(body.password)

    vendor = Vendor(email=body.email, password_hash=hashed_pw)
    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    return {"message":"Vendor created ", "data":vendor }  # FastAPI + Pydantic handles serialization safely


# ----------- LOGIN VENDOR -----------
@router.post("/login")
def login_vendor(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    vendor = db.query(Vendor).filter(Vendor.email == form_data.username).first()
    if not vendor:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not argon2.verify(form_data.password, vendor.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_vendor_token({"sub": vendor.email})
    return {"access_token": token, "token_type": "bearer"}


# ----------- GET CURRENT VENDOR PROFILE -----------
@router.get("/me", response_model=VendorResponse)
def get_vendor_profile(token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    vendor = db.query(Vendor).filter(Vendor.email == email).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    return vendor   # Pydantic takes care of exposing safe fields
