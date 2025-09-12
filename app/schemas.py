from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional ,List

class WorkerBase(BaseModel):
    id: str
    access: str
    email: EmailStr

class WorkerCreate(WorkerBase):
    pass

class WorkerOut(WorkerBase):
    class Config:
        from_attributes = True

class FarmBase(BaseModel):
    id: int
    address: Optional[str] = None
    longitude: Optional[str] = None
    latitude: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    farmname: Optional[str] = None
    area: Optional[str] = None

class FarmOut(FarmBase):

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: EmailStr
    phone: Optional[str] = None
    profilepicture: Optional[str] = None
    nin: Optional[str] = None
    kyc_status: str = "unverified"
    emailverified: bool = False
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserCreate(UserBase):
    farm: Optional[FarmBase] = None
    workers: Optional[List[WorkerCreate]] = []

class UserOut(UserBase):
    id: int
    farm: Optional[FarmOut]
    workers: List[WorkerOut] = []
    class Config:
        from_attributes = True

#
#
# class UserBase(BaseModel):
#     email: EmailStr
#     id: int
#
#
# class UserCreate(UserBase):
#     password: str
#     first_name: Optional[str]
#     last_name: Optional[str]
#     gender: Optional[str]
#
# class UserLogin(BaseModel):
#     email: EmailStr
#     password: str
#
# class UserProfileUpdate(BaseModel):
#     id: int
#     email: EmailStr
#     # full_name:str | None = None
#     bio: str | None = None
#     gender: str | None = None
#     first_name:str | None = None
#     myfarm: str | None = None
#     last_name: str | None = None
#     location:str | None = None
#     profilepicture:str | None = None
#
#     class Config:
#         from_attributes = True  # ✅ Pydantic v2 (use orm_mode=True if on v1)
#
# class UserProfileResponse(BaseModel):
#     message: str
#     data: UserProfileUpdate
#
#
#
# class UserOut(UserBase):
#     id: int
#     email: str
#     first_name: Optional[str] = None
#     last_name: Optional[str] = None
#     phone: Optional[str] = None
#     # id: int
#     # full_name: Optional[str]
#     # bio: Optional[str]
#     # profile_completed: bool
#     # first_name: Optional[str]
#     # last_name: Optional[str]
#     # gender: Optional[str]
#
#     class Config:
#         from_attributes = True  # ✅ replaces orm_mode
#
#
# class UserLearning(BaseModel):
#     id: int
#     user_id: int    # ma
#     status : Optional[str] = None
#     email: Optional[str] = None
#     first_question: Optional[str] = None
#     second_question: Optional[str] = None
#     video_lenght: Optional[str] = None
#     fourth_question: Optional[str] = None
#
#     class Config:
#         from_attributes = True  # ✅ replaces orm_mode
#
#
# class ShowmyFarm(BaseModel):
#     id: int
#     user_id: int  # ma
#     farm_name:str
#     farm_image: Optional[str] = None
#     # email: Optional[str] = None
#
#     class Config:
#         from_attributes = True  # ✅ replaces orm_mode










class PondBase(BaseModel):
    record_id: int
    user_id: int
    user_farm: int
    pond_name: str
    pond_type: str
    pond_capacity: str
    pond_image_path: str


class PondCreate(PondBase):
    """Schema for creating a new pond"""
    pass  # inherits everything from PondBase


class PondUpdate(BaseModel):
    """Schema for updating pond details"""
    pond_name: Optional[str] = None
    pond_type: Optional[str] = None
    pond_capacity: Optional[str] = None
    pond_image_path: Optional[str] = None
    user_farm: Optional[int] = None


class PondOut(PondBase):
    """Schema for returning pond info"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # ✅ for SQLAlchemy -> Pydantic conversion