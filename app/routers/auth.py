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
from ..dep.security import create_tokens
router = APIRouter(prefix="/auth", tags=["auth"])

class RegisterIn(BaseModel):
    first_name: str
    gender: Optional[str] = None
    last_name: str
    email: EmailStr | None = None
    phone: str | None = None
    password: str

@router.get("/allusers", response_model=List[UserOut])
def getUser(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@router.post("/register")
def register(body: RegisterIn, db: Session = Depends(get_db)):
    if not body.email and not body.phone:
        raise HTTPException(400, "email or phone required")
    if body.email and db.query(User).filter(User.email == body.email).first():
        raise HTTPException(409, "email exists")
    if body.phone and db.query(User).filter(User.phone == body.phone).first():
        raise HTTPException(409, "phone exists")
    u = User(
        email=body.email,
        phone=body.phone,
        first_name=body.first_name,  # add this
        last_name=body.last_name,  # add this
        gender=body.gender,  # optional
        password_hash=argon2.hash(body.password),
        roles=["user"]
    )
    db.add(u); db.commit(); db.refresh(u)
    return {"user_id": str(u.id)}

class LoginIn(BaseModel):
    email: Optional[EmailStr] = None
    phone: str | None = None
    password: str

class LoginOut(BaseModel):
    id: int
    email: str
    access: str
    refresh: str
    token_type: str = "bearer"

@router.post("/login", response_model=LoginOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = None
    if body.email:
        user = db.query(User).filter(User.email == body.email).first()
    elif body.phone:
        user = db.query(User).filter(User.phone == body.phone).first()

    if not user or not argon2.verify(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    tokens = create_tokens(user.id)
    return {
        "id": user.id,
        "email": user.email,
        "access": tokens["access"],
        "refresh": tokens["refresh"],
        "token_type": "bearer"
    }

# @router.post("/login")
# def login(body: LoginIn, db: Session = Depends(get_db)):
#     user = None
#     if body.email:
#         user = db.query(User).filter(User.email == body.email).first()
#     elif body.phone:
#         user = db.query(User).filter(User.phone == body.phone).first()
#     if not user or not argon2.verify(body.password, user.password_hash):
#         raise HTTPException(401, "invalid credentials")
#     return create_tokens(user.id)  # user.id must exist in DB
#
