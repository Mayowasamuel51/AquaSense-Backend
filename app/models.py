from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Numeric, Date
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
    gender = Column(String(222), nullable=True)
    email_verified = Column(Boolean, default=False)
    profilepicture = Column(Boolean , nullable=True)
    password_hash = Column(String(255), nullable=False)
    nin = Column(String(50), nullable=True)
    location = Column(String(50), nullable=True)
    kyc_status = Column(String(50), default="unverified")
    first_name = Column(String(100))
    last_name = Column(String(100))

    roles = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class MyFarm(Base):
    __tablename__ = "myfarm"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    farm_name = Column(String(520), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)



class Learn(Base):
    __tablename__ = "learns"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(50), default="pending")
    video_lenght = Column(String(52220), nullable=False)
    first_question = Column(String(52220), nullable=False)
    second_question = Column(String(52220), nullable=False)
    third_question = Column(String(52220), nullable=False)
    fourth_question = Column(String(52220), nullable=False)


class Record(Base):
    __tablename__ = "units"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    unit_name = Column(String(520), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class Pond (Base):
    __tablename__ = "ponds"
    id = Column(Integer, primary_key=True, autoincrement=True)
    record_id = Column(Integer, ForeignKey("units.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    pond_name= Column(String(520), nullable=False)
    pond_type = Column(String(520),  nullable=False)
    pond_capacity = Column(String(520),  nullable=False)
    pond_image_path  = Column(String(520),  nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
#

class IncomeFarm(Base):
    __tablename__ = "income"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    income_type = Column(String(520), nullable=False)
    amountearn = Column(Integer, nullable=False)
    quantity_sold = Column(Integer, nullable=False)
    total_fish_cost = Column(Integer, nullable=False)
    which_pond = Column(String(520), nullable=False)
    income_date = Column(DateTime, nullable=False)
    payment_method = Column(String(520), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)



# class PondInfo (Base):
#     __tablename__ = "pondsinfo"
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     pond_id = Column(Integer, ForeignKey("ponds.id"), nullable=False)
#     record_id = Column(Integer, ForeignKey("records.id"), nullable=False)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#
#     fish_type = Column(String(520), nullable=False)
#     stock_pond_date  = fish_date = Column(Date, nullable=False)
#     number_fish = Column(Integer, nullable=False)
#     total_fish_cost = Column(Integer, nullable=False)
#     ba= Column(Integer, nullable=False)
#
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow)


#
# class PondData (Base):
#     __tablename__ = "pondsinfo"
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     pond_id = Column(Integer, ForeignKey("ponds.id"), nullable=False)
#     record_id = Column(Integer, ForeignKey("records.id"), nullable=False)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     pondinfo_id = Column(Integer, ForeignKey("pondsinfos.id"), nullable=False)
#
#     feed_name = Column(String(520), nullable=False)
#     feed_size  = fish_date = Column(Integer, nullable=False)
#     feed_quantity= Column(Integer, nullable=False)
#     mortality = Column(Integer, default=0)
#     submitted_at = Column(DateTime, default=datetime.utcnow)
#     status = Column(String(50), default="pending")
#
#     user = relationship("User", back_populates="pond_data")
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow)





class Wallet(Base):
    __tablename__ = "wallets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    balance = Column(Numeric(12,2), default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class Otp(Base):
    __tablename__ = "otps"
    id = Column(Integer, primary_key=True, autoincrement=True)
    channel = Column(String(520))
    target = Column(String(300), index=True)
    code_hash = Column(String(2323))
    expires_at = Column(DateTime)
    attempts = Column(Integer, default=0)
    used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)