from datetime import datetime, timezone, timedelta
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Admin
from ..config import settings

security = HTTPBearer()

# ---------------------------
# Global JWT Config
# ---------------------------
JWT_SECRET = settings.JWT_SECRET
JWT_REFRESH_SECRET = settings.JWT_REFRESH_SECRET
ACCESS_TTL = 800   # days for access
REFRESH_TTL = 780  # days for refresh

# ---------------------------
# ✅ USER TOKENS (unchanged)
# ---------------------------
def create_token(subject: int, secret: str, days: int):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=days)).timestamp())
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def create_tokens(user_id: int):
    return {
        "access_token": create_token(user_id, JWT_SECRET, ACCESS_TTL),
        "refresh_token": create_token(user_id, JWT_REFRESH_SECRET, REFRESH_TTL),
    }


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = creds.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = int(payload.get("sub"))
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token is invalid")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


# =============================================================
# ✅ ADMIN TOKENS (separate logic — user untouched)
# =============================================================

def _create_admin_token(admin_id: int, secret: str, days: int):
    """Internal helper for admin-specific tokens."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(admin_id),
        "role": "admin",  # distinct claim
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=days)).timestamp())
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def create_admin_tokens(admin_id: int):
    """Generate admin access + refresh tokens."""
    return {
        "access_token": _create_admin_token(admin_id, JWT_SECRET, ACCESS_TTL),
        "refresh_token": _create_admin_token(admin_id, JWT_REFRESH_SECRET, REFRESH_TTL),
    }


def get_current_admin(
    creds: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Validate admin token & return admin instance."""
    token = creds.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        admin_id = int(payload.get("sub"))
        role = payload.get("role")
        if role != "admin":
            raise HTTPException(status_code=403, detail="Invalid token role for admin")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token is invalid")

    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if not admin:
        raise HTTPException(status_code=401, detail="Admin not found")

    return admin


# ---------------------------
# EMAIL VERIFICATION TOKEN
# ---------------------------
VERIFY_TOKEN_TTL = 300000

def create_verification_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": int(now.timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")




# from datetime import datetime, timezone, timedelta
# import jwt
# from fastapi import Depends, HTTPException, status
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from sqlalchemy.orm import Session
# from ..database import get_db
# from ..models import User
# from ..config import settings
#
# security = HTTPBearer()
# # python-jose[cryptography]
# # Secret keys (use from settings.py or .env)
# JWT_SECRET = settings.JWT_SECRET
# JWT_REFRESH_SECRET = settings.JWT_REFRESH_SECRET
#
# # Token lifetimes in daysa
# ACCESS_TTL = 800   # 120 days for access
# REFRESH_TTL = 780  # 180 days for refresh
#
#
# # ✅ create a token
# def create_token(subject: int, secret: str, days: int):
#     now = datetime.now(timezone.utc)
#     payload = {
#         "sub": str(subject),   # store user id correctly
#         "iat": int(now.timestamp()),
#         "exp": int((now + timedelta(days=days)).timestamp())
#     }
#     return jwt.encode(payload, secret, algorithm="HS256")
#
#
# # ✅ create access + refresh tokens
# def create_tokens(user_id: int):
#     return {
#         "access_token": create_token(user_id, JWT_SECRET, ACCESS_TTL),
#         "refresh_token": create_token(user_id, JWT_REFRESH_SECRET, REFRESH_TTL),
#     }
#
#
# # ✅ extract current user from token
# def get_current_user(
#     creds: HTTPAuthorizationCredentials = Depends(security),
#     db: Session = Depends(get_db)
# ):
#     token = creds.credentials
#     try:
#         payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
#         user_id = int(payload.get("sub"))
#     except jwt.ExpiredSignatureError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Token has expired"
#         )
#     except jwt.PyJWTError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Token is invalid"
#         )
#
#     user = db.query(User).filter(User.id == user_id).first()
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="User not found"
#         )
#
#     return user
#
# # from jose import jwt
# # Verification token lifetime (e.g. 30 minutes)
# VERIFY_TOKEN_TTL = 300000
#
# def create_verification_token(user_id: int) -> str:
#     """
#     Create a short-lived JWT token for email verification
#     """
#     now = datetime.now(timezone.utc)
#     payload = {
#         "sub": str(user_id),
#         "iat": int(now.timestamp()),
#         # "exp": int((now + timedelta(minutes=VERIFY_TOKEN_TTL)).timestamp())
#     }
#     return jwt.encode(payload, JWT_SECRET, algorithm="HS256")
