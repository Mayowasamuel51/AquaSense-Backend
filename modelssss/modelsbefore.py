from sqlalchemy import Column, Integer, String, Boolean, Text
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # Authentication
    email = Column(String(255), unique=True, index=True)         # 255 is standard for email
    hashed_password = Column(String(255))                        # password hashes usually fit in 255
    is_active = Column(Boolean, default=True)

    # Profile fields
    first_name = Column(String(100), nullable=True)              # names usually under 100 chars
    last_name = Column(String(100), nullable=True)
    gender = Column(String(20), nullable=True)                   # "male", "female", "other" etc.
    full_name = Column(String(200), nullable=True)               # safer to allow longer than first/last
    bio = Column(Text, nullable=True)                            # Text allows large bios
    profile_completed = Column(Boolean, default=False)
