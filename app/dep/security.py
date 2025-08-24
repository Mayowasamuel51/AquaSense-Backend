from datetime import datetime, timedelta
import jwt, os
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer
from passlib.hash import argon2
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..config import settings

security = HTTPBearer()

ACCESS_TTL = 15  # minutes
REFRESH_TTL = 14 * 24 * 60  # minutes

class TokenPair(BaseModel):
    access: str
    refresh: str

def create_token(subject: str, secret: str, minutes: int):
    now = datetime.utcnow()
    payload = {"sub": subject, "iat": int(now.timestamp()), "exp": int((now + timedelta(minutes=minutes)).timestamp())}
    return jwt.encode(payload, secret, algorithm="HS256")

def create_tokens(user_id: str) -> TokenPair:
    return TokenPair(
        access=create_token(user_id, settings.JWT_SECRET, ACCESS_TTL),
        refresh=create_token(user_id, settings.JWT_REFRESH_SECRET, REFRESH_TTL),
    )