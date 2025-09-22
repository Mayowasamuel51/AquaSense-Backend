from urllib.parse import quote_plus, unquote_plus

from fastapi import APIRouter, Depends, HTTPException , status
from pydantic import BaseModel, EmailStr , ConfigDict ,  model_validator
from typing import Optional ,  List
from sqlalchemy.orm import Session
from passlib.hash import argon2
import smtplib

from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from ..database  import get_db
from datetime import datetime, timedelta
from jinja2 import Template
from ..models import User, VerificationToken, Farm, JustData
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
EMAIL_ADDRESS = "aquasenseapp@gmail.com"       # change to your email
EMAIL_PASSWORD  = "xnnz pxum rxoq cnaz"          # use app password (not raw Gmail pass)

# def send_verification_email(to_email: str, verify_url: str):
#     msg = EmailMessage()
#     msg['Subject'] = "Verify your AquaSense account"
#     msg['From'] = EMAIL_ADDRESS
#     msg['To'] = to_email
#
#     # msg.set_content(f"""
#     # Hi,
#     # Please verify your AquaSense account by clicking the link below:
#     # {verify_url}
#     # If you did not request this, you can safely ignore it.
#     # """)
#
#     try:
#         with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
#             smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
#             smtp.send_message(msg)
#             logger.info(f"Verification email sent to {to_email}")
#     except Exception as e:
#         logger.info(f"Verification email sent to {to_email}")
#         raise Exception(f"Failed to send verification email: {e}")

EMAIL_HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Verify Your Email - AquaSense+</title>
  <style>
    body, table, td, a {
      -webkit-text-size-adjust: 100%;
      -ms-text-size-adjust: 100%;
    }
    body {
      margin: 0;
      padding: 0;
      background-color: #f4f4f4;
      font-family: Arial, sans-serif;
    }
    table {
      border-collapse: collapse !important;
    }
    .container {
      max-width: 600px;
      margin: 40px auto;
      background-color: #ffffff;
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .header {
      background-color: #276882;
      padding: 20px;
      text-align: center;
      color: #ffffff;
      font-size: 24px;
      font-weight: bold;
    }
    .content {
      padding: 30px;
      text-align: center;
      color: #333333;
    }
    .button {
      display: inline-block;
      padding: 14px 28px;
      margin: 20px 0;
      background-color: #276882;
      color: #ffffff !important;
      font-size: 16px;
      font-weight: bold;
      text-decoration: none;
      border-radius: 6px;
    }
    .footer {
      background-color: #f9f9f9;
      padding: 15px;
      text-align: center;
      font-size: 12px;
      color: #888888;
    }
    a {
      color: #276882;
    }
  </style>
</head>
<body>
  <table width="100%">
    <tr>
      <td>
        <div class="container">
          <div class="header">
            AquaSense+
          </div>
          <div class="content">
            <h2>Hi {{ full_name }},</h2>
            <p>Thank you for registering with <strong>AquaSense+</strong>!</p>
            <p>Please verify your email address to complete your registration and activate your account.</p>

            <!-- ✅ Deep link button -->
            <a href="{{ deep_link }}"    style="display:inline-block;
          padding:14px 28px;
          margin:20px 0;
          background-color:#276882;
          color:#ffffff !important;
          font-size:16px;
          font-weight:bold;
          text-decoration:none;
          border-radius:6px;" class="button">Verify Email</a>

            <p>If the button doesn’t work, copy and paste this link into your browser:</p>
            <p><a href="{{ web_link }}">{{ web_link }}</a></p>
          </div>
          <div class="footer">
            If you didn’t sign up for AquaSense, you can safely ignore this email.
          </div>
        </div>
      </td>
    </tr>
  </table>
</body>
</html>
"""

def send_verification_email(to_email: str, token: str, full_name: str ):
    msg = EmailMessage()
    msg['Subject'] = "Verify your AquaSense account"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email

    # Links
    deep_link = f"aquasense://verify?token={token}"
    web_link = f"https://aquasense-backend-jsa5.onrender.com/api/v1/auth/verify?token={token}"

    # ✅ Plain text fallback
    msg.set_content(f"""\
    Hi {full_name},

    Thank you for registering with AquaSense!

    Please verify your email by opening this link in the app:
    {deep_link}

    If that doesn’t work, copy and paste this link into your browser:
    {web_link}

    If you didn’t sign up, you can safely ignore this email.
    """)

    # ✅ Render HTML with Jinja2
    template = Template(EMAIL_HTML_TEMPLATE)
    html_content = template.render(full_name=full_name, deep_link=deep_link, web_link=web_link)

    # Attach HTML version
    msg.add_alternative(html_content, subtype="html")
    print(html_content)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
            logger.info(f"Verification email sent to {to_email}")
    except Exception as e:
        logger.error(f"Failed to send verification email: {e}")
        raise Exception(f"Failed to send verification email: {e}")



class RegisterIn(BaseModel):
    first_name: str
    last_name: str
    gender: str
    email: EmailStr
    phone: Optional[str] = None
    password: str
    access : Optional[str] = None


class FarmOut(BaseModel):
    id: int
    farmname: str
    farmtype: str
    owner_id: int

    class Config:
        from_attributes = True

class UserOutResponse(BaseModel):
    message: str
    user: UserOut




@router.post("/register")
def register(body: RegisterIn, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    if body.email and db.query(User).filter(User.email == body.email).first():
        raise HTTPException(409, "email exists")

    u = User(
        email=body.email,
        phone=body.phone,
        first_name=body.first_name,
        last_name=body.last_name,
        gender=body.gender,
        password_hash=argon2.hash(body.password),
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    display_name = f"{u.first_name or ''} {u.last_name or ''}".strip() or u.email.split("@")[0]
    jd = JustData(user_id=u.id, display_name=display_name)
    db.add(jd)
    db.commit()

    # Generate verification token
    token = create_verification_token(u.id)

    # Send email in background
    background_tasks.add_task(send_verification_email, body.email, token, jd.display_name)

    db_token = VerificationToken(
        token=token,
        user_id=u.id,
    )


    db.add(db_token)
    db.commit()


    return {
        "user_id": u.id,
        "data": u,
        # "token": token,
        "access_token": token,
        "message": "User registered successfully. Please check your email to verify your account."
    }



@router.get("/verify", response_class=HTMLResponse)
def verify_email(token: str, db: Session = Depends(get_db)):
    # decode token from URL (handles %2E, +, etc)
    token = unquote_plus(token)

    # find token row
    vt = db.query(VerificationToken).filter(VerificationToken.token == token).one_or_none()
    if not vt:
        raise HTTPException(400, "Invalid token")

    # fetch user
    user = db.query(User).filter(User.id == vt.user_id).one_or_none()
    if not user:
        raise HTTPException(400, "User not found")

    # mark verified if needed
    if not user.email_verified:
        user.email_verified = True
        db.commit()
        message = "Email verified successfully!"
    else:
        message = "User already verified!"

    # prepare deep-link and web link (encode token for URL)
    deep_link = f"aquasense://verify?token={quote_plus(vt.token)}"
    web_link = f"https://aquasense-backend-jsa5.onrender.com/api/v1/auth/verify?token={quote_plus(vt.token)}"

    # simple, clean HTML
    html = f"""
    <!doctype html>
    <html>
    <head>
      <meta charset="utf-8"/>
      <meta name="viewport" content="width=device-width,initial-scale=1"/>
      <title>AquaSense — Email Verified</title>
      <style>
        body {{ font-family: system-ui, -apple-system, "Segoe UI", Roboto, Arial; background:#f3f6f9; color:#0b1a2b; margin:0; padding:24px; }}
        .card {{ max-width:720px; margin:48px auto; background:#fff; border-radius:12px; padding:28px; box-shadow:0 10px 30px rgba(11,26,43,0.08); }}
        h1 {{ margin:0 0 6px; font-size:24px; }}
        p.lead {{ margin:10px 0 20px; color:#334155; }}
        .actions {{ display:flex; gap:12px; flex-wrap:wrap; }}
        .btn {{ padding:12px 18px; border-radius:8px; text-decoration:none; font-weight:600; display:inline-block; }}
        .btn-primary {{ background:#0ea5a7; color:#fff; }}
        .btn-ghost {{ background:transparent; border:1px solid #e6eef0; color:#0b1a2b; }}
        .info {{ margin-top:18px; background:#fbfdfe; padding:12px; border-radius:8px; color:#475569; font-size:14px; }}
        code {{ display:block; margin-top:8px; padding:10px; background:#0b1a2b; color:#e6fffa; border-radius:6px; word-break:break-all; }}
      </style>
    </head>
    <body>
      <div class="card">
        <h1>✅ {message}</h1>
        <p class="lead">Hi {user.first_name or user.email}, your email {user.email} is verified. Thanks for joining AquaSense.</p>

        <div class="actions">
          <a class="btn btn-primary" href="{deep_link}">Open App</a>
          <a class="btn btn-ghost" href="{web_link}">Open App Web</a>
        </div>

        <div class="info">
          <div><strong>User:</strong> {user.first_name or ''} {user.last_name or ''} &nbsp; • &nbsp; {user.email}</div>
          <div style="margin-top:10px;"><strong>Verification token (for mobile app):</strong></div>
          <code>{vt.token}</code>
        </div>
      </div>
    </body>
    </html>
    """

    return HTMLResponse(content=html, status_code=200)


# @router.get("/verify")
# def verify_email(token: str, db: Session = Depends(get_db)):
#     # Find the verification token
#     vt = db.query(VerificationToken).filter(
#         VerificationToken.token == token
#     ).one_or_none()
#
#     if not vt:
#         raise HTTPException(400, "Invalid token")
#
#     # ✅ Fetch the user tied to this token
#     user = db.query(User).filter(User.id == vt.user_id).one_or_none()
#     if not user:
#         raise HTTPException(400, "User not found")
#
#     # Mark user as verified
#     if not user.emailverified:
#         user.emailverified = True
#         db.commit()
#
#     return {
#         "message": (
#             "Email verified successfully!"
#             if user.emailverified else "User already verified!"
#         ),
#         "data": {
#             "id": user.id,
#             "email": user.email,
#             "first_name": user.first_name,
#             "last_name": user.last_name,
#             "phone": user.phone,
#             "gender": user.gender,
#             "kyc_status": user.kyc_status,
#             "profilepicture": user.profilepicture,
#             "nin": user.nin,
#             "coins": user.coins,
#             "emailverified": user.emailverified,
#             "access_token": vt.token,   # keep token in response for the mobile app
#         },
#     }


# @router.get("/verify")
# def verify_email(token: str, db: Session = Depends(get_db)):
#     vt = db.query(VerificationToken).filter(VerificationToken.token == token).first()
#     if not vt:
#         raise HTTPException(400, "Invalid token")
#     if vt.expires_at < datetime.utcnow():
#         raise HTTPException(400, "Token expired")
#
#     # ✅ Fetch the correct user
#     user = db.query(User).filter(User.id == vt.user_id).first()
#     if not user:
#         raise HTTPException(400, "User not found")
#
#     user.email_verified = True
#     db.delete(vt)  # remove token after use
#     db.commit()
#
#     return {
#         "message": "Email verified successfully!",
#         "data": {
#             "id": user.id,
#             "email": user.email,
#             "first_name": user.first_name,
#             "last_name": user.last_name,
#             "phone": user.phone,
#             "gender": user.gender,
#             "kyc_status": user.kyc_status,
#             "profilepicture": user.profilepicture,
#             "nin": user.nin,
#             "coins": user.coins,
#             "email_verified": user.email_verified,
#         },
#     }
@router.post("/resend-verification" , response_model=UserOutResponse)
def resend_verification_email(
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.id == user.id).one_or_none()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # 1. Check if already verified
    if db_user.emailverified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified"
        )

    # 2. Generate a new token
    token = create_verification_token(db_user.id)

    # 3. Save the new token (✅ keep old ones, don’t delete)
    db_token = VerificationToken(
        token=token,
        user_id=db_user.id,
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)

    # 4. Prepare verification link
    verify_url = f"https://aquasense-backend-jsa5.onrender.com/api/v1/auth/verify?token={token}"

    # 5. Send email in background
    background_tasks.add_task(send_verification_email, db_user.email, token,
                              f"{db_user.first_name} {db_user.last_name}")

    return {"message": "Verification email resent successfully",token:token,  "user": UserOut.from_orm(db_user) }



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
    if not user.emailverified:
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
