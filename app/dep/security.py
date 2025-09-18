from datetime import datetime, timezone, timedelta
import jwt
# from jose import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..config import settings

security = HTTPBearer()
# python-jose[cryptography]
# Secret keys (use from settings.py or .env)
JWT_SECRET = settings.JWT_SECRET
JWT_REFRESH_SECRET = settings.JWT_REFRESH_SECRET

# Token lifetimes in days
ACCESS_TTL = 800   # 120 days for access
REFRESH_TTL = 780  # 180 days for refresh


# ✅ create a token
def create_token(subject: int, secret: str, days: int):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(subject),   # store user id correctly
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=days)).timestamp())
    }
    return jwt.encode(payload, secret, algorithm="HS256")


# ✅ create access + refresh tokens
def create_tokens(user_id: int):
    return {
        "access_token": create_token(user_id, JWT_SECRET, ACCESS_TTL),
        "refresh_token": create_token(user_id, JWT_REFRESH_SECRET, REFRESH_TTL),
    }


# ✅ extract current user from token
def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = creds.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = int(payload.get("sub"))
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


# Verification token lifetime (e.g. 30 minutes)
VERIFY_TOKEN_TTL = 300000

def create_verification_token(user_id: int) -> str:
    """
    Create a short-lived JWT token for email verification
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": int(now.timestamp()),
        # "exp": int((now + timedelta(minutes=VERIFY_TOKEN_TTL)).timestamp())
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")
