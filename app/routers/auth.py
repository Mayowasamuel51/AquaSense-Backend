from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from passlib.hash import argon2
from uuid import uuid4
from ..database  import get_db
from ..models import User
from ..dep.security import create_tokens

router = APIRouter(prefix="/auth", tags=["auth"])

class RegisterIn(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr | None = None
    phone: str | None = None
    password: str

@router.post("/register")
def register(body: RegisterIn, db: Session = Depends(get_db)):
    if not body.email and not body.phone:
        raise HTTPException(400, "email or phone required")
    if body.email and db.query(User).filter(User.email == body.email).first():
        raise HTTPException(409, "email exists")
    if body.phone and db.query(User).filter(User.phone == body.phone).first():
        raise HTTPException(409, "phone exists")
    u = User(email=body.email, phone=body.phone, password_hash=argon2.hash(body.password), roles=["user"])
    db.add(u); db.commit(); db.refresh(u)
    return {"user_id": str(u.id)}

class LoginIn(BaseModel):
    email: EmailStr | None = None
    phone: str | None = None
    password: str

@router.post("/login")
def login(body: LoginIn, db: Session = Depends(get_db)):
    q = None
    if body.email:
        q = db.query(User).filter(User.email == body.email).first()
    elif body.phone:
        q = db.query(User).filter(User.phone == body.phone).first()
    if not q or not argon2.verify(body.password, q.password_hash):
        raise HTTPException(401, "invalid credentials")
    return create_tokens(str(q.id)).dict()