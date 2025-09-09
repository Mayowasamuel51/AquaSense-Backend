from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr , ConfigDict ,  model_validator

from typing import Optional ,  List
from sqlalchemy.orm import Session
from passlib.hash import argon2

from ..database  import get_db
from ..models import User
from ..schemas import UserOut
from ..dep.security import create_tokens , get_current_user
router = APIRouter(prefix="/auth", tags=["auth"])
print(11)

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
    return {
        "user_id": str(u.id) ,
        "message":"user registered successfully",
        "data":u
    }
#


class LoginIn(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str

    @ model_validator(mode="after")
    def at_least_one_identifier(self):
        if not self.email and not self.phone:
            raise ValueError("Either email or phone must be provided")
        return self


class UserOut(BaseModel):
    id: int
    email: str
    phone: Optional[str] = None
    profilepicture: Optional[str] = None
    nin: Optional[str] = None
    location: Optional[str] = None
    kyc_status: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserIn(BaseModel):
    email: EmailStr
    phone: str
    password: str
    profilepicture: Optional[str] = None
    nin: Optional[str] = None
    location: Optional[str] = None
    kyc_status: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class LoginOut(BaseModel):
    id: int
    email: str
    access: str
    refresh: str
    token_type: str = "bearer"
    data: UserOut


# ---------- Route ----------

@router.post("/login",  response_model=LoginOut)
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
        "token_type": "bearer",
        "data": user,  # Auto-converted to UserOut
    }

# class LoginIn(BaseModel):
#     email: Optional[EmailStr] = None
#     phone: Optional[str] = None
#     password: str
#
#     # password: str
#
#
# class UserOut(BaseModel):
#     id: int
#     email: str
#     phone: Optional[str] = None
#     class Config:
#         orm_mode = True  # important for SQLAlchemy models
#
#
# class UserIn(BaseModel):
#     email: EmailStr
#     phone: str
#     password: str
#     profilepicture: Optional[str] = None
#     nin: Optional[str] = None
#     location: Optional[str] = None
#     kyc_status: Optional[str] = None
#     first_name: Optional[str] = None
#     last_name: Optional[str] = None
#
# class LoginOut(BaseModel):
#     id: int
#     email: str
#     access: str
#     refresh: str
#     token_type: str = "bearer"
#     data: UserIn   # 🔥 new field for user info
#
# @router.post("/login", response_model=LoginOut)
# def login(body: LoginIn, db: Session = Depends(get_db)):
#     user = None
#     if body.email:
#         user = db.query(User).filter(User.email == body.email).first()
#     elif body.phone:
#         user = db.query(User).filter(User.phone == body.phone).first()
#     if not user or not argon2.verify(body.password, user.password_hash):
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#     tokens = create_tokens(user.id)
#
#     return {
#         "data": user,
#         "id": user.id,
#         "email": user.email,
#         "access": tokens["access"],
#         "refresh": tokens["refresh"],
#         "token_type": "bearer"
#     }

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
