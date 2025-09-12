from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Numeric, Date ,Text
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime , timedelta
import uuid
from .database import Base
import random

number = int("".join(str(d) for d in random.sample(range(0, 10), 5)))
def generate_random_number():
    # Make a random 5-digit number (digits won’t repeat inside the number)
    return "".join(str(d) for d in random.sample(range(0, 10), 5))


class Farm(Base):
    __tablename__ = "farms"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    address = Column(String(255), nullable=True)
    longitude = Column(String(100), nullable=True)
    latitude = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    farmname = Column(String(255), nullable=True)
    area = Column(String(100), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))  # links to User


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(50), nullable=True)
    profilepicture = Column(String(255), nullable=True )
    nin = Column(String(50), nullable=True)
    email_verified = Column(Boolean, default=False)
    kyc_status = Column(String(50), default="unverified")
    # emailverified = Column(Boolean, default=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    gender = Column(String(50), nullable=True)
    password_hash = Column(String(255), nullable=False)
    # roles = Column(JSON, default=["user"])  # stored as JSON array in MySQL
    farm = relationship("Farm", uselist=False, backref="owner")
    workers = relationship("Worker", back_populates="user")
    # relationship to tokens
    tokens = relationship("VerificationToken", back_populates="user")


class VerificationToken(Base):
    __tablename__ = "verification_tokens"
    id = Column(Integer,primary_key=True, index=True, autoincrement=True)
    token = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    expires_at = Column(DateTime, default=lambda: datetime.datetime.utcnow() + datetime.timedelta(hours=1))
    user = relationship("User", back_populates="tokens")


class Worker(Base):
    __tablename__ = "workers"
    id = Column(String(100), primary_key=True, index=True)  # from JSON
    access = Column(Text, nullable=False)
    email = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="workers")

#
# class Learn(Base):
#     __tablename__ = "learns"
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     status = Column(String(50), default="pending")
#     video_lenght = Column(String(52220), nullable=False)
#     first_question = Column(String(52220), nullable=False)
#     second_question = Column(String(52220), nullable=False)
#     third_question = Column(String(52220), nullable=False)
#     fourth_question = Column(String(52220), nullable=False)

# class IncomeFarm(Base):
#     __tablename__ = "income"
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     pond_name = Column(Integer, ForeignKey("ponds.id"), nullable=False)
#     income_type = Column(String(520), nullable=False)
#     amountearn = Column(Integer, nullable=False)
#     quantity_sold = Column(Integer, nullable=False)       #we should know auto
#     total_fish_cost = Column(Integer, nullable=False)     #we should know auto
#     which_pond = Column(String(520), nullable=False)      #we should know auto
#     income_date = Column(DateTime, nullable=False)
#     payment_method = Column(String(520), nullable=False)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow)



# class User(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     email = Column(String(255), unique=True, index=True, nullable=True)
#     phone = Column(String(20), unique=True, index=True, nullable=True)
#     phone_verified = Column(Boolean, default=False)
#     gender = Column(String(222), nullable=True)
#     bio = Column(String(2232), nullable=True)
#     email_verified = Column(Boolean, default=False)
#     profilepicture = Column(Boolean , nullable=True)
#     password_hash = Column(String(255), nullable=False)
#     nin = Column(String(50), nullable=True)
#     location = Column(String(50), nullable=True)
#     kyc_status = Column(String(50), default="unverified")
#     first_name = Column(String(100))
#     last_name = Column(String(100))
#
#     roles = Column(JSON, default=list)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow)
#
#
# class MyFarm(Base):
#     __tablename__ = "farm"
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     farm_image = Column(String(520), nullable=True)
#     farm_name = Column(String(520), nullable=True)
#     farm_type= Column(String(520),  nullable=True)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow)
#
# class Batch(Base):
#     __tablename__ = "batches"
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     user_farm = Column(Integer, ForeignKey("farm.id"), nullable=False)
#     batch_track_number= Column(String(10), unique=True, nullable=False ,  default=generate_random_number )
#     batch_name = Column(String(520), unique=True, nullable=False)
#     batch_capacity= Column(String(2444), nullable=False)
#     batch_option = Column(String(520),  nullable=False)
#     batch_option_2 = Column(String(520), nullable=False)
#
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow)




# class Pond (Base):
#     __tablename__ = "ponds"
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     record_id = Column(Integer, ForeignKey("units.id"), nullable=False)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     user_farm= Column(Integer, ForeignKey("farm.id"), nullable=False)
#     batch = Column(Integer, ForeignKey("batches.id"), nullable=False)
#     pond_name= Column(String(520),  unique=True ,nullable=False)
#     pond_track_number = Column(String(10),nullable=False, default=generate_random_number)
#     pond_type = Column(String(520),  nullable=False)
#     pond_capacity = Column(String(520),  nullable=False)
#     pond_image_path  = Column(String(520),  nullable=False)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow)
# #
#
# class Record(Base):
#     __tablename__ = "units"
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     unit_name = Column(String(520), nullable=False)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow)





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


# class Wallet(Base):
#     __tablename__ = "wallets"
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     balance = Column(Numeric(12,2), default=0)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow)
#
# class Otp(Base):
#     __tablename__ = "otps"
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     channel = Column(String(520))
#     target = Column(String(300), index=True)
#     code_hash = Column(String(2323))
#     expires_at = Column(DateTime)
#     attempts = Column(Integer, default=0)
#     used_at = Column(DateTime, nullable=True)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow)