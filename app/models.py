from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
import uuid
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    phone = Column(String(20), unique=True, index=True, nullable=True)
    phone_verified = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False)
    password_hash = Column(String(255), nullable=False)
    nin = Column(String(50), nullable=True)
    kyc_status = Column(String(50), default="unverified")
    first_name = Column(String(100))
    last_name = Column(String(100))
    roles = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    balance = Column(Numeric(12,2), default=0)

class Otp(Base):
    __tablename__ = "otps"
    id = Column(Integer, primary_key=True, autoincrement=True)
    channel = Column(String(520))
    target = Column(String(300), index=True)
    code_hash = Column(String(2323))
    expires_at = Column(DateTime)
    attempts = Column(Integer, default=0)
    used_at = Column(DateTime, nullable=True)