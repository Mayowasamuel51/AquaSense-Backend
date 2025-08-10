from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    first_name: Optional[str]
    last_name: Optional[str]
    gender: Optional[str]

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserProfileUpdate(BaseModel):
    full_name: Optional[str]
    bio: Optional[str]
    gender: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]

class UserOut(UserBase):
    id: int
    full_name: Optional[str]
    bio: Optional[str]
    profile_completed: bool
    first_name: Optional[str]
    last_name: Optional[str]
    gender: Optional[str]

    class Config:
        orm_mode = True
