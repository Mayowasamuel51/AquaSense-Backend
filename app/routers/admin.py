from datetime import datetime, timedelta
import os, secrets, string
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from passlib.hash import argon2
import resend

from ..database import get_db
from ..models import Admin, AdminOTP, User, Vendor
from ..dep.security import create_admin_tokens, get_current_admin  # ✅ Updated imports
from ..schemas import VendorResponse

router = APIRouter(prefix="/admin", tags=["Admin Auth"])

# ---------------- CONFIG ----------------
OTP_EXPIRY_MINUTES = int(os.getenv("ADMIN_OTP_EXPIRY", 90))
ADMIN_CREATE_SECRET = os.getenv("ADMIN_CREATE_SECRET", "supersecret")

RESEND_API_KEY = os.getenv("RESEND_API_KEY", "re_TbGCTK88_9jiyARuZAhPfcANEoESZdTx5")
resend.api_key = RESEND_API_KEY
RESEND_FROM_EMAIL = os.getenv(
    "RESEND_FROM_EMAIL", "AquaSense+ <noreply@apimypromospheretest.com.ng>"
)


# ---------------- SCHEMAS ----------------
class AdminLogin(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class ForgotPassword(BaseModel):
    email: EmailStr


class VerifyOTP(BaseModel):
    email: EmailStr
    otp: str
    new_password: str = Field(min_length=8)


class CreateAdmin(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None
    secret: str | None = None


class AdminOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None
    is_super: bool

    class Config:
        from_attributes = True


# ---------------- HELPERS ----------------
def generate_numeric_otp(length: int = 6):
    return "".join(secrets.choice(string.digits) for _ in range(length))


def hash_value(value: str):
    return argon2.hash(value)


def verify_hash(value: str, hashed: str):
    try:
        return argon2.verify(value, hashed)
    except Exception:
        return False


# ---------------- ROUTES ----------------

@router.post("/create", response_model=AdminOut)
def create_admin(data: CreateAdmin, db: Session = Depends(get_db)):
    """Create a new admin (protected by a shared secret)."""
    if data.secret != ADMIN_CREATE_SECRET:
        raise HTTPException(status_code=403, detail="Invalid creation secret")

    exists = db.query(Admin).filter(Admin.email == data.email).first()
    if exists:
        raise HTTPException(status_code=400, detail="Admin already exists")

    hashed_pw = argon2.hash(data.password)
    admin = Admin(
        email=data.email,
        password_hash=hashed_pw,
        full_name=data.full_name,
        is_super=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin

@router.post("/register", response_model=AdminOut)
def register_admin(data: CreateAdmin, db: Session = Depends(get_db)):
    """
    Public admin registration (no secret key).
    Use only if you want open registration for admins.
    """
    exists = db.query(Admin).filter(Admin.email == data.email).first()
    if exists:
        raise HTTPException(status_code=400, detail="Admin already exists")

    hashed_pw = argon2.hash(data.password)
    admin = Admin(
        email=data.email,
        password_hash=hashed_pw,
        full_name=data.full_name,
        is_super=False  # regular admin, not super by default
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)

    return admin

@router.post("/login")
def admin_login(data: AdminLogin, db: Session = Depends(get_db)):
    """Admin login route with profile + tokens."""
    admin = db.query(Admin).filter(Admin.email == data.email).first()
    if not admin or not argon2.verify(data.password, admin.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Generate access + refresh tokens
    tokens = create_admin_tokens(admin.id)

    return {
        "admin": {
            "id": admin.id,
            "email": admin.email,
            "full_name": admin.full_name,
            "is_super": admin.is_super,
            "created_at": admin.created_at,
        },
        "tokens": tokens
    }


@router.post("/forgot-password")
def admin_forgot_password(data: ForgotPassword, db: Session = Depends(get_db)):
    """Send OTP via Resend for password reset."""
    admin = db.query(Admin).filter(Admin.email == data.email).first()
    # Always respond 200 to prevent email enumeration
    if not admin:
        return {"detail": "If this email exists, an OTP has been sent"}

    otp = generate_numeric_otp()
    otp_hash = hash_value(otp)
    expiry = datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)

    otp_entry = AdminOTP(
        admin_id=admin.id,
        email=admin.email,
        otp_hash=otp_hash,
        expires_at=expiry
    )
    db.add(otp_entry)
    db.commit()

    # Send OTP email using Resend
    html = f"""
    <h2>Password Reset Code</h2>
    <p>Hello {admin.full_name or admin.email},</p>
    <p>Your OTP is:</p>
    <h1>{otp}</h1>
    <p>This code expires in {OTP_EXPIRY_MINUTES} minutes.</p>
    """

    try:
        resend.Emails.send({
            "from": RESEND_FROM_EMAIL,
            "to": admin.email,
            "subject": "Admin Password Reset Code",
            "html": html
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email failed: {e}")

    return {"detail": "If this email exists, an OTP has been sent"}


@router.post("/verify-otp")
def admin_verify_otp(data: VerifyOTP, db: Session = Depends(get_db)):
    """Verify OTP and reset password."""
    otp_record = (
        db.query(AdminOTP)
        .filter(AdminOTP.email == data.email, AdminOTP.used == False)
        .order_by(AdminOTP.created_at.desc())
        .first()
    )
    if not otp_record:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    if otp_record.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP expired")

    if not verify_hash(data.otp, otp_record.otp_hash):
        raise HTTPException(status_code=400, detail="Invalid OTP")

    admin = db.query(Admin).filter(Admin.email == data.email).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    admin.password_hash = argon2.hash(data.new_password)
    otp_record.used = True
    db.commit()

    return {"detail": "Password reset successful"}


@router.get("/me", response_model=AdminOut)
def admin_me(current_admin: Admin = Depends(get_current_admin)):
    """Return current authenticated admin info."""
    return current_admin
class VendorMainListin(BaseModel):
    message:str
    data:List[VendorResponse]


@router.get("/allvendors", response_model=VendorMainListin )
def getUser(db: Session = Depends(get_db)):
    vendors  = db.query(Vendor).all()
    return {"message":"showing all Vendors", "data": vendors}