from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr , ConfigDict ,  model_validator
from typing import Optional ,  List
from sqlalchemy.orm import Session
from passlib.hash import argon2
import smtplib
from ..database  import get_db
from datetime import datetime, timedelta
from ..models import User , VerificationToken , Farm
from ..schemas import UserOut
from ..dep.security import create_tokens , get_current_user , create_verification_token , create_token
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import os
from email.message import EmailMessage
import logging
from fastapi import BackgroundTasks
logger = logging.getLogger("uvicorn.error")
router = APIRouter(prefix="/auth", tags=["auth"])
print(11123)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "fpasamuelmayowa51@gmail.com"       # change to your email
EMAIL_PASSWORD  = "cvzy htcq fzsa tybs"          # use app password (not raw Gmail pass)

def send_verification_email(to_email: str, verify_url: str):
    msg = EmailMessage()
    msg['Subject'] = "Verify your AquaSense account"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email

    msg.set_content(f"""
    Hi,
    Please verify your AquaSense account by clicking the link below:
    {verify_url}
    If you did not request this, you can safely ignore it.
    """)
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
            logger.info(f"Verification email sent to {to_email}")
    except Exception as e:
        logger.info(f"Verification email sent to {to_email}")
        raise Exception(f"Failed to send verification email: {e}")

class RegisterIn(BaseModel):
    first_name: str
    last_name: str
    gender: str
    email: str
    phone: Optional[str] = None
    password: str
    access : Optional[str] = None


@router.post("/register")
def register(body: RegisterIn,background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    if body.email and db.query(User).filter(User.email == body.email).first():
        raise HTTPException(409, "email exists")
    u = User(
        email=body.email,
        phone=body.phone,
        first_name=body.first_name,
        last_name=body.last_name,
        gender=body.gender,
        password_hash=argon2.hash(body.password),
        # roles=["user"]
    )

    # create empty farm
    # farm = Farm(
    #     address="",
    #     longitude="",
    #     latitude="",
    #     city="",
    #     state="",
    #     farmname="",
    #     area=""
    # )
    # u.farm = farm



    db.add(u); db.commit(); db.refresh(u)
    token = create_verification_token(u.id)
    db_token = VerificationToken(
        token=token,
        user_id=u.id,
        expires_at=datetime.utcnow() + timedelta(minutes=30)
    )
    db.add(db_token)
    db.commit()
    verify_url = f"http://127.0.0.1:8000/api/v1/auth/verify?token={token}"

    # send verification email in background
    background_tasks.add_task(send_verification_email, body.email, verify_url)


    # send verification email
    # try:
    #     # send_verification_email(body.email, verify_url)
    # except Exception as e:
    #     raise HTTPException(500, f"Failed to send verification email: {str(e)}")

    return {
        "user_id": u.id,
        "data":u,
        "token":token,
        "message": "User registered successfully. Please check your email to verify your account."
    }

@router.get("/verify")
def verify_email(token: str, db: Session = Depends(get_db)):
    vt = db.query(VerificationToken).filter(VerificationToken.token == token).first()
    if not vt:
        raise HTTPException(400, "Invalid token")
    if vt.expires_at < datetime.utcnow():
        raise HTTPException(400, "Token expired")

    user = vt.user
    user.email_verified = True
    db.delete(vt)  # remove token after use
    db.commit()

    return {"message": "Email verified successfully!"}

@router.get("/allusers", response_model=List[UserOut])
def getUser(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users


class LoginIn(BaseModel):
    email: EmailStr
    password: str

class LoginOut(BaseModel):
    user: UserOut
    token_type: str = "bearer"
    access_token: str
    refresh_token: Optional[str] = None

@router.post("/login", response_model=LoginOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    # 1. Get user
    user = db.query(User).filter(User.email == body.email).first()
    if not user:
        raise HTTPException(401, "Invalid email or password")

    # 2. Check password
    if not argon2.verify(body.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")

    # 3. Check email verified
    if not user.email_verified:
        raise HTTPException(403, "Please verify your email before logging in")

    # 4. Create tokens
    tokens = create_tokens(user.id)
    # return {
    #     "access_token": tokens["access_token"],
    #     "refresh_token": tokens["refresh_token"],
    #     "user": UserOut.from_orm(user)
    # }
    # 5. Return full user data + tokens
    return {
        "user": UserOut.model_validate(user),
        "token_type": "bearer",
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
    }
    # return {
    #     "user": {
    #         "id": user.id,
    #         "email": user.email,
    #         "first_name": user.first_name,
    #         "last_name": user.last_name,
    #         # ✅ reference the relationship directly
    #         "farm": {
    #             "id": user.farm.id if user.farm else None,
    #             "farmname": user.farm.farmname if user.farm else None,
    #             "address": user.farm.address if user.farm else None,
    #             "longitude": user.farm.longitude if user.farm else None,
    #             "latitude": user.farm.latitude if user.farm else None,
    #             "city": user.farm.city if user.farm else None,
    #             "state": user.farm.state if user.farm else None,
    #             "area": user.farm.area if user.farm else None,
    #         }
    #     },
    #     "tokens": tokens
    # }














# class LoginIn(BaseModel):
#     email: Optional[EmailStr] = None
#     phone: Optional[str] = None
#     password: str
#
#     # @ model_validator(mode="after")
#     # def at_least_one_identifier(self):
#     #     if not self.email and not self.phone:
#     #         raise ValueError("Either email or phone must be provided")
#     #     return self
#
#
# class UserOut(BaseModel):
#     id: int
#     email: str
#     phone: Optional[str] = None
#     profilepicture: Optional[str] = None
#     nin: Optional[str] = None
#     location: Optional[str] = None
#     kyc_status: Optional[str] = None
#     first_name: Optional[str] = None
#     last_name: Optional[str] = None
#     model_config = ConfigDict(from_attributes=True)

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
#     model_config = ConfigDict(from_attributes=True)
#
# class LoginOut(BaseModel):
#     id: int
#     email: str
#     access: str
#     refresh: str
#     token_type: str = "bearer"
#     data: UserOut
#
#
# # ---------- Route ----------

# @router.post("/login",  response_model=LoginOut)
# def login(body: LoginIn, db: Session = Depends(get_db)):
#     user = None
#     if body.email:
#         user = db.query(User).filter(User.email == body.email).first()
#     if not user or not argon2.verify(body.password, user.password_hash):
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#     tokens = create_tokens(user.id)
#     return {
#         "id": user.id,
#         "email": user.email,
#         "access": tokens["access"],
#         "refresh": tokens["refresh"],
#         "token_type": "bearer",
#         "data": user,  # Auto-converted to UserOut
#     }

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
