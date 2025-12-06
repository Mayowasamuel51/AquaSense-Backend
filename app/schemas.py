from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict, HttpUrl ,  Field, constr, validator
from typing import Optional ,List


# ---------- CONTACT ----------
class ContactBase(BaseModel):
    name: str
    email: EmailStr
    message: str

class ContactCreate(ContactBase):
    pass

class ContactResponse(ContactBase):
    id: int
    email:str
    message:str
    class Config:
        from_attributes = True

# ---------- WAIT ----------
class WaitBase(BaseModel):
    firstname: str
    email: EmailStr

class WaitCreate(WaitBase):
    pass

class WaitResponse(WaitBase):
    id: int
    firstname: str
    email: str
    class Config:
        from_attributes = True

class WaitBase(BaseModel):
    firstname: str
    email: EmailStr

class WaitCreate(WaitBase):
    pass

class WaitResponse(WaitBase):
    id: int
    firstname :str
    email :str
    class Config:
        from_attributes = True


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
    farmtype:Optional[str] = None
    area: Optional[str] = None

class FarmOut(FarmBase):

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: EmailStr
    # user_cluster_name:Optional[str] = None
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
    coins:int         # i just add this here for the labs
    email:str
    # cluster_name:str
    farm: Optional[FarmOut]
    workers: List[WorkerOut] = []
    class Config:
        from_attributes = True



class UserOutForProduct(UserBase):
    id: int
    # coins:int         # i just add this here for the labs
    email:str
    farm: Optional[FarmOut]
    workers: List[WorkerOut] = []
    class Config:
        from_attributes = True



class LocationUpdate(BaseModel):
    address: Optional[str] = None
    longitude: Optional[str] = None
    latitude: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    area: Optional[str] = None




class OptionOut(BaseModel):
    id: int
    text: str

    class Config:
        from_attributes = True

class TestOut(BaseModel):
    id: int
    question: str
    options: List[OptionOut]
    correct_option_id: int


    class Config:
        from_attributes = True

class VideoOut(BaseModel):
    id: int
    title: str
    description: str
    video_url: str
    thumbnail_url: Optional[str]
    coins: int
    duration_in_seconds: int
    is_watched: bool = False  # default

    class Config:
        from_attributes = True

class ModuleOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    videos: List[VideoOut]
    tests: List[TestOut]

    total_coins: int
    completion_bonus_coins: int

    class Config:
        from_attributes = True

class AnswerTestIn(BaseModel):
    test_id: int
    option_id: int

class UnitBase(BaseModel):
    pondName: str
    pondType: str
    pondCapacity: int
    fishes: int
    imageUrl: Optional[str] = None
    type: Optional[str] = None
    isActive: Optional[bool] = False


class UnitResponse(UnitBase):

    id: str
    farmerId: int
    createdAt: datetime
    updatedAt: Optional[datetime]

    class Config:
        from_attributes = True
class UnitCreate(UnitBase):
   pass
   # message: str
   # unit:UnitResponse

   class Config:
        from_attributes = True


class BatchBase(BaseModel):
    batchName: str
    fishtype: Optional[str] = None
    numberoffishes: Optional[int] = None
    isCompleted: Optional[bool] = False

class BatchCreate(BatchBase):
    # farmerId: int
    pass
class BatchResponse(BatchBase):
    batchId: str
    farmerId: int
    fishtype:Optional[str] = None
    numberoffishes:Optional[str] = None
    # isCompleted:Optional[str] = None
    # isCompleted = str
    createdAt:Optional[datetime]
    updatedAt: Optional[datetime]

    class Config:
        from_attributes = True

class RecordBase(BaseModel):
    batchId: str
    unitId: str

class RecordCreate(RecordBase):
    farmerId: int

class RecordResponse(RecordBase):
    id: str
    farmerId: int
    createdAt: datetime
    updatedAt: Optional[datetime]
    unit: UnitResponse  # nested unit
    dailyRecords: List["DailyRecordResponse"] = []
    weightSamplings: List["WeightSamplingResponse"] = []
    gradingAndSortings: List["GradingAndSortingResponse"] = []
    harvests: List["HarvestFormResponse"] = []

    class Config:
        from_attributes = True

class DailyRecordBase(BaseModel):
    date: datetime
    feedName: str
    feedSize: str
    feedQuantity: float
    mortality: int
    coins: Optional[int] = None

class DailyRecordCreate(DailyRecordBase):
    feedName: str
    feedSize: str
    feedQuantity: float
    mortality: int
    date: datetime
    # batchId: str  # ✅ required so we know where to attach the record
    # unitId: str  # ✅ required so we know which pond/cage
    # feedName: str
    # feedSize: str
    # feedQuantity: float
    # mortality: int
    # date: datetime
    # batchId: str   # required so we know where to attach the record
    # unitId: str    # required so we know which pond/cage
#
class DailyRecordResponse(DailyRecordBase):
    id: str
    farmerId: int
    batchId: str
    unitId: str
    recordId: str
    coins: Optional[int]
    createdAt: datetime
    updatedAt:datetime

    class Config:
        from_attributes = True


class WeightSamplingBase(BaseModel):
    sampleName: str
    date: datetime
    fishNumbers: int
    totalWeight: float
    completed: bool

class WeightSamplingCreate(WeightSamplingBase):
    farmerId: int
    batchId: str
    unitId: str
    recordId: str

class WeightSamplingResponse(WeightSamplingBase):
    recordId: str
    farmerId: int
    batchId: str
    unitId: str
    createdAt: datetime

    class Config:
        from_attributes = True


class GradeBase(BaseModel):
    destinationBatchId: Optional[str] = None
    destinationBatchName: Optional[str] = None
    destinationUnitId: str
    destinationUnitName: str
    averageFishWeight: float
    fishTransferred: int

class GradeCreate(GradeBase):
    gradingAndSortingId: str

class GradeResponse(GradeBase):
    id: int

    class Config:
        from_attributes = True


class GradingAndSortingBase(BaseModel):
    gradeWith: str
    sampleName: str
    date: datetime
    gradingPondNumber: int
    fishNumbers: int
    totalWeight: float
    completed: bool

class GradingAndSortingCreate(GradingAndSortingBase):
    farmerId: int
    batchId: str
    unitId: str
    recordId: str

class GradingAndSortingResponse(GradingAndSortingBase):
    recordId: str
    farmerId: int
    batchId: str
    unitId: str
    createdAt: datetime
    grades: List[GradeResponse] = []

    class Config:
        from_attributes = True

class HarvestFormBase(BaseModel):
    date: datetime
    harvestedWeight: float
    harvestedFish: int

class HarvestFormCreate(HarvestFormBase):
    farmerId: int
    batchId: str
    unitId: str
    recordId: str

class HarvestFormResponse(HarvestFormBase):
    recordId: str
    farmerId: int
    batchId: str
    unitId: str
    createdAt: datetime

    class Config:
        from_attributes = True


class FeedBase(BaseModel):
    feedName: str
    feedForm: str
    feedSize: str
    quantity: int
    # unit: str
    unitMeasure: str
    costPerUnit: float
    totalAmount: float
    date: datetime

class FeedCreate(FeedBase):
    batchId: str
    unitId: str

class FeedResponse(FeedBase):
    id: str
    farmerId: int
    batchId: str
    unitId: str
    createdAt: datetime
    updatedAt: Optional[datetime]

    class Config:
        from_attributes = True



class IncomeBase(BaseModel):
    incomeType: str
    amountEarned: float
    quantitySold: int
    paymentMethod: str
    incomeDate: datetime
    appliedToPondName: Optional[str] = None   # ✅

class IncomeCreate(IncomeBase):
    batchId: str
    unitId: str

class IncomeResponse(IncomeBase):
    # id: str
    # farmerId: int
    # batchId: str
    # unitId: str
    # createdAt: datetime
    # updatedAt: Optional[datetime]
    id: str
    farmerId: int
    farmId: int
    batchId: str
    unitId: str
    harvestId: Optional[str] = None
    appliedToPondName: Optional[str] = None
    createdAt: datetime
    updatedAt: Optional[datetime]

    class Config:
        from_attributes = True


class StockingBase(BaseModel):
    fishType: str
    quantityPurchased: int
    totalAmount: float
    date: datetime
    appliedToPondName: Optional[str] = None  # ✅ helps mobile dev

class StockingCreate(StockingBase):
    batchId: str
    unitId: str

class StockingResponse(StockingBase):
    id: str
    farmerId: int
    batchId: str
    unitId: str
    farmId: int
    createdAt: datetime
    updatedAt: Optional[datetime]

    class Config:
        from_attributes = True

class CategoryBase(BaseModel):
    name: str
    model_config = dict(from_attributes=True)

class CategoryOut(CategoryBase):
    id: int


# class PriceRangeBase(BaseModel):
#     from_: float = Field(..., alias="from")
#     to: float
#     class Config:
#         from_attributes = True
#         validate_by_name = True  #
#
# class ProductTypeBase(BaseModel):
#     typeValue: str
#     valueMeasurement: str
#     valuePrice: float
#     quantity: int = 0
#     class Config:
#         from_attributes = True
#
# class ProductCreate(BaseModel):
#     title: str
#     description: Optional[str]
#     image: Optional[str]
#     price: float
#     category: str
#     priceRange: Optional[PriceRangeBase] = Field(None, alias="price_range")
#     types: Optional[List[ProductTypeBase]] = []   # 👈 optional with default empty list
#
# class ProductOut(ProductCreate):
#     id: int
#     priceRange: Optional[PriceRangeBase] = Field(None, alias="price_range")
#     class Config:
#         from_attributes = True
#
# class CartCreate(BaseModel):
#     product_id: int
#     quantity: int
#     type_id: Optional[int] = None
#
# class CartOut(BaseModel):
#     id: int
#     quantity: int
#     product: ProductOut
#     selected_type: Optional[ProductTypeBase]
#
#     class Config:
#         from_attributes = True



class PriceRange(BaseModel):
    from_: Optional[float] = None
    to: Optional[float] = None
    class Config:
        fields = {"from_": "from"}  # allows "from" in JSON input

class ProductTypeCreate(BaseModel):
    typeValue: str
    valueMeasurement: Optional[str] = None
    valuePrice: float


class ProductCreate(BaseModel):
    title: str
    description: Optional[str] = None
    image: Optional[HttpUrl] = None
    price: float
    category: str
    price_range: Optional[PriceRange] = None
    discount_percent: Optional[float] = 0.0
    discount_amount: Optional[float] = 0.0
    types: List[ProductTypeCreate]


class ProductTypeResponse(BaseModel):
    id: int
    type_value: str
    value_measurement: Optional[str]
    value_price: float

    class Config:
        from_attributes = True


class ProductResponse(BaseModel):
    id: int
    vendor_id: int  # ✅ Add this
    title: str
    description: Optional[str]
    image: Optional[str]
    price: float
    category: str
    price_from: Optional[float]
    price_to: Optional[float]
    discount_percent: Optional[float]
    discount_amount: Optional[float]
    types: List[ProductTypeResponse]

    class Config:
        from_attributes = True

# class VendorRegister(BaseModel):
#     email: EmailStr
#     password: str
class VendorRegister(BaseModel):
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    profilepicture: Optional[str] = None
    gender: Optional[str] = None
    # nin: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    area: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None


# ----------------- RESPONSE MODELS -----------------
class VendorResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    profilepicture: Optional[str] = None
    gender: Optional[str] = None
    nin: Optional[str] = None
    kyc_status: Optional[str] = None
    emailverified: Optional[bool] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    area: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    # first_name:str
    # last_name: Optional[str] = None
    # phone: str
    # profilepicture: Optional[str] = None
    # gender: str
    # nin: Optional[str] = None
    # kyc_status: Optional[str] = None
    # emailverified: Optional[bool] = None
    # address: Optional[str] = None
    # city: Optional[str] = None
    # state: str
    # area: Optional[str] = None
    # latitude: Optional[str] = None
    # longitude: Optional[str] = None



    class Config:
        from_attributes = True   # allows returning SQLAlchemy models directly



class VetImageResponse(BaseModel):
    id: int
    url: str

    class Config:
        from_attributes = True

class VetVideoResponse(BaseModel):
    id: int
    url: str

    class Config:
        from_attributes = True

class VetSupportCreate(BaseModel):
    helpwith: constr(min_length=5, max_length=250) = Field(..., description="Description of the issue or help needed")
    # images: constr(min_length=5, max_length=250) = Field(..., description="you cant upload more than 3 images")
    issue: constr(min_length=5, max_length=250) = Field(..., description="Description of the issue or help needed")
    modeofsupport : constr(min_length=5, max_length=250) = Field(..., description="Description of the mode of support  or help needed")
    date: constr(min_length=3, max_length=50) = Field(..., description="Date string, e.g. 2025-10-12")
    # coins: constr(regex=r"^\d+$") = Field(..., description="Number of coins to use (digits only)")

    @validator("helpwith")
    def validate_helpwith(cls, v):
        if not v.strip():
            raise ValueError("helpwith field cannot be empty")
        return v

    @validator("issue")
    def validate_helpwith(cls, v):
        if not v.strip():
            raise ValueError("issue  field cannot be empty")
        return v


class VetUserInfo(BaseModel):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    profilepicture: Optional[str] = None

    class Config:
        from_attributes = True


class VetSupportResponse(BaseModel):
    id: int
    helpwith: Optional[str] = None
    date: Optional[str] = None
    modeofsupport: Optional[str] =None
    issue:Optional[str] = None
    images: List[VetImageResponse] = []
    videos: List[VetVideoResponse] = []
    user: Optional[VetUserInfo] = None

    class Config:
        from_attributes = True
# class CartItem(BaseModel):
#     product_id: str
#     quantity: int
#
# class CartOut(BaseModel):
#     product: ProductOut
#     quantity: int
#     total_price: float
#
#     class Config:
#         from_attributes = True




# class ProductOut(ProductCreate):
#     id: int
#     priceRange:PriceRangeBase
#     model_config = dict(
#         from_attributes=True,
#         validate_by_name=True
#     )
    # class Config:
    #     from_attributes = True
    #     fields = {
    #         "priceRange": "price_range"
    #     }

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