from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    id: int

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
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    # id: int
    # full_name: Optional[str]
    # bio: Optional[str]
    # profile_completed: bool
    # first_name: Optional[str]
    # last_name: Optional[str]
    # gender: Optional[str]

    class Config:
        from_attributes = True  # ✅ replaces orm_mode


class UserLearning(BaseModel):
    id: int
    user_id: int    # ma
    status : Optional[str] = None
    email: Optional[str] = None
    first_question: Optional[str] = None
    second_question: Optional[str] = None
    video_lenght: Optional[str] = None
    fourth_question: Optional[str] = None

    class Config:
        from_attributes = True  # ✅ replaces orm_mode


class ShowmyFarm(BaseModel):
    id: int
    user_id: int  # ma
    farm_name:str
    # email: Optional[str] = None

    class Config:
        from_attributes = True  # ✅ replaces orm_mode