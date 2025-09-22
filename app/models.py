from numbers import Integral

from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Numeric, Date, Text, Float
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

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), nullable=False, index=True)
    message = Column(Text, nullable=False)

class Wait(Base):
    __tablename__ = "waitlist"

    id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String(100), nullable=False)
    email = Column(String(120), nullable=False, index=True)




class Farm(Base):
    __tablename__ = "farms"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    address = Column(String(255), nullable=True)
    longitude = Column(String(100), nullable=True)
    latitude = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    farmname = Column(String(255), nullable=True)
    farmtype = Column(String(255), nullable=True)
    area = Column(String(100), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id") ,  unique=True)
    # relationship
    # incomes = relationship("Income", back_populates="farm")
    incomes = relationship("Income", back_populates="farm")  # ✅
    stockings = relationship("Stocking", back_populates="farm")

    # incomes = relationship("Income", back_populates="farmer", cascade="all, delete-orphan")

    # links to User

class JustData(Base):
    __tablename__ = "justdata"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    display_name = Column(String(250), nullable=True)
    # relationship back to User
    user = relationship("User", back_populates="justdata")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(50), nullable=True)
    profilepicture = Column(String(255), nullable=True )
    nin = Column(String(50), nullable=True)

    kyc_status = Column(String(50), default="unverified")
    emailverified = Column(Boolean, default=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    gender = Column(String(50), nullable=True)
    coins = Column(Integer, default=0)

    # ✅ Progress relationships
    justdata = relationship("JustData", back_populates="user", uselist=False)
    password_hash = Column(String(255), nullable=False)
    # roles = Column(JSON, default=["user"])  # stored as JSON array in MySQL
    farm = relationship("Farm", uselist=False, backref="owner")
    workers = relationship("Worker", back_populates="user")
    # relationship to tokens
    tokens = relationship("VerificationToken", back_populates="user")
    # ✅ relationships
    video_progress = relationship("UserVideoProgress", backref="user", cascade="all, delete-orphan")
    test_progress = relationship("UserTestProgress", back_populates="user", cascade="all, delete-orphan")
    # Farming units, batches, and records , feeds,
    units = relationship("Unit", back_populates="farmer")
    batches = relationship("Batch", back_populates="farmer")
    records = relationship("Record", back_populates="farmer")
    feeds = relationship("Feed", back_populates="farmer")  # <-- 🔥 new one
    # User model
    incomes = relationship("Income", back_populates="farmer", cascade="all, delete-orphan")
    stockings = relationship("Stocking", back_populates="farmer")
    # ✅ add this only once
    # incomes = relationship("Income", back_populates="farmer")


class VerificationToken(Base):
    __tablename__ = "verification_tokens"
    id = Column(Integer,primary_key=True, index=True, autoincrement=True)
    token = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    # expires_at = Column(DateTime, default=lambda: datetime.datetime.utcnow() + datetime.timedelta(hours=2))
    user = relationship("User", back_populates="tokens")

class Worker(Base):
    __tablename__ = "workers"
    id = Column(String(100), primary_key=True, index=True)  # from JSON
    access = Column(Text, nullable=False)
    email = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="workers")

class Module(Base):
    __tablename__ = "modules"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    total_coins = Column(Integer, default=0)
    completion_bonus_coins = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    videos = relationship("Video", back_populates="module", cascade="all, delete-orphan")
    tests = relationship("Test", back_populates="module", cascade="all, delete-orphan")

class Video(Base):
    __tablename__ = "videos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=False)
    title = Column(String(255), nullable=False)
    video_url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500), nullable=True)
    description = Column(String(800), nullable=True)
    coins = Column(Integer, default=0)
    duration_in_seconds = Column(Integer, nullable=True)

    module = relationship("Module", back_populates="videos")

class Test(Base):
    __tablename__ = "tests"
    id = Column(Integer, primary_key=True, autoincrement=True)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=False)
    question = Column(Text, nullable=False)
    correct_option_id = Column(Integer, ForeignKey("options.id"), nullable=True)
    coins = Column(Integer, default=10)
    module = relationship("Module", back_populates="tests")
    options = relationship("Option", back_populates="test", cascade="all, delete-orphan",
                           foreign_keys="Option.test_id")
    progresses = relationship("UserTestProgress", back_populates="test", cascade="all, delete-orphan")

class Option(Base):
    __tablename__ = "options"
    id = Column(Integer, primary_key=True, autoincrement=True)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False)
    text = Column(String(255), nullable=False)

    test = relationship("Test", back_populates="options", foreign_keys=[test_id])

class UserVideoProgress(Base):
    __tablename__ = "user_video_progress"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False)
    is_watched = Column(Boolean, default=False)
    earned_coins = Column(Integer, default=0)

class UserTestAnswer(Base):
    __tablename__ = "user_test_answers"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False)  # matches Test.id
    selected_option_id = Column(Integer, ForeignKey("options.id"), nullable=True)
    answered_at = Column(DateTime, default=datetime.utcnow)

class UserTestProgress(Base):
    __tablename__ = "user_test_progress"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False)

    # ✅ FIXED: make this an INTEGER foreign key
    selected_option_id = Column(Integer, ForeignKey("options.id"), nullable=True)

    is_correct = Column(Boolean, nullable=True)
    earned_coins = Column(Integer, default=0)

    # ✅ relationships
    user = relationship("User", back_populates="test_progress")
    test = relationship("Test", back_populates="progresses")
    selected_option = relationship("Option", foreign_keys=[selected_option_id])

class Unit(Base):
    __tablename__ = "units"

    id = Column(String(50), primary_key=True, index=True)
    farmerId = Column(Integer, ForeignKey("users.id"), nullable=False)
    pondName = Column(String(100), nullable=False)
    pondType = Column(String(50), nullable=False)  # e.g., Earthen, Concrete
    pondCapacity = Column(Integer, nullable=False)
    fishes = Column(Integer, nullable=False)
    imageUrl = Column(String(255))
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=None)
    type = Column(String(50))  # e.g., "Cage" or "Pond"
    isActive = Column(Boolean, default=False)
    # ✅ Add feeds relationship
    feeds = relationship("Feed", back_populates="unit")
    farmer = relationship("User", back_populates="units")
    records = relationship("Record", back_populates="unit")
    # Unit model

    incomes = relationship("Income", back_populates="unit")
    # In Unit
    stockings = relationship("Stocking", back_populates="unit")


class Batch(Base):
    __tablename__ = "batches"
    batchId = Column(String(50), primary_key=True, index=True)
    farmerId = Column(Integer, ForeignKey("users.id"), nullable=False)
    batchName = Column(String(100), nullable=False)
    fishtype = Column(String(100), nullable=False)
    numberoffishes = Column(String(100), nullable=False)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=None)
    isCompleted = Column(Boolean, default=False)
    farmer = relationship("User", back_populates="batches")
    records = relationship("Record", back_populates="batch")
    # ✅ Add feeds relationship
    feeds = relationship("Feed", back_populates="batch")
    # Batch model

    incomes = relationship("Income", back_populates="batch")   # ✅ matches Income.batch
    # In Batch
    stockings = relationship("Stocking", back_populates="batch")


class Record(Base):
    __tablename__ = "records"

    id = Column(String(50), primary_key=True, index=True)
    farmerId = Column(Integer, ForeignKey("users.id"), nullable=False)
    batchId = Column(String(50), ForeignKey("batches.batchId"))
    unitId = Column(String(50), ForeignKey("units.id"))

    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    unit = relationship("Unit", back_populates="records")
    batch = relationship("Batch", back_populates="records")
    farmer = relationship("User", back_populates="records")

    dailyRecords = relationship("DailyRecord", back_populates="record")
    weightSamplings = relationship("WeightSampling", back_populates="record")
    gradingAndSortings = relationship("GradingAndSorting", back_populates="record")
    harvests = relationship("HarvestForm", back_populates="record")

class DailyRecord(Base):
    __tablename__ = "daily_records"

    id = Column(String(50), primary_key=True, index=True)   # PK UUID
    recordId = Column(String(50), ForeignKey("records.id")) # FK to records
    farmerId = Column(Integer, ForeignKey("users.id"), nullable=False)
    batchId = Column(String(50), ForeignKey("batches.batchId"))
    unitId = Column(String(50), ForeignKey("units.id"))

    date = Column(DateTime, nullable=False)
    feedName = Column(String(100), nullable=False)
    feedSize = Column(String(50), nullable=False)
    feedQuantity = Column(Float, nullable=False)
    mortality = Column(Integer, nullable=False)
    coins = Column(Integer, default=None)

    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    record = relationship("Record", back_populates="dailyRecords")

class WeightSampling(Base):
    __tablename__ = "weight_samplings"

    recordId = Column(String(50), ForeignKey("records.id"), primary_key=True)
    farmerId = Column(Integer, ForeignKey("users.id"), nullable=False)
    batchId = Column(String(50), ForeignKey("batches.batchId"))
    unitId = Column(String(50), ForeignKey("units.id"))
    sampleName = Column(String(100))
    date = Column(DateTime, nullable=False)
    fishNumbers = Column(Integer, nullable=False)
    totalWeight = Column(Float, nullable=False)
    completed = Column(Boolean, default=False)
    createdAt = Column(DateTime, default=datetime.utcnow)

    record = relationship("Record", back_populates="weightSamplings")

class Grade(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, autoincrement=True)
    gradingAndSortingId = Column(String(50), ForeignKey("grading_and_sortings.recordId"))
    destinationBatchId = Column(String(50), nullable=True)
    destinationBatchName = Column(String(100), nullable=True)
    destinationUnitId = Column(String(50), nullable=False)
    destinationUnitName = Column(String(100), nullable=False)
    averageFishWeight = Column(Float, nullable=False)
    fishTransferred = Column(Integer, nullable=False)

class GradingAndSorting(Base):
    __tablename__ = "grading_and_sortings"

    recordId = Column(String(50), ForeignKey("records.id"), primary_key=True)
    farmerId = Column(Integer, ForeignKey("users.id"), nullable=False)
    batchId = Column(String(50), ForeignKey("batches.batchId"))
    unitId = Column(String(50), ForeignKey("units.id"))
    gradeWith = Column(String(50))
    sampleName = Column(String(100))
    date = Column(DateTime, nullable=False)
    gradingPondNumber = Column(Integer)
    fishNumbers = Column(Integer)
    totalWeight = Column(Float)
    completed = Column(Boolean, default=False)
    createdAt = Column(DateTime, default=datetime.utcnow)

    record = relationship("Record", back_populates="gradingAndSortings")
    grades = relationship("Grade", backref="gradingAndSorting")

class HarvestForm(Base):
    __tablename__ = "harvests"

    recordId = Column(String(50), ForeignKey("records.id"), primary_key=True)
    farmerId = Column(Integer, ForeignKey("users.id"), nullable=False)
    batchId = Column(String(50), ForeignKey("batches.batchId"))
    unitId = Column(String(50), ForeignKey("units.id"))
    date = Column(DateTime, nullable=False)
    harvestedWeight = Column(Float, nullable=False)
    harvestedFish = Column(Integer, nullable=False)
    createdAt = Column(DateTime, default=datetime.utcnow)

    record = relationship("Record", back_populates="harvests")

class Feed(Base):
    __tablename__ = "feeds"

    id = Column(String(50), primary_key=True, index=True)
    farmerId = Column(Integer, ForeignKey("users.id"), nullable=False)

    batchId = Column(String(50), ForeignKey("batches.batchId"), nullable=False)
    unitId = Column(String(50), ForeignKey("units.id"), nullable=False)

    feedName = Column(String(100), nullable=False)
    feedForm = Column(String(50), nullable=False)
    feedSize = Column(String(50), nullable=False)
    quantity = Column(Integer, nullable=False)
    # unit = Column(String(50), nullable=False)
    unitMeasure = Column(String(50), nullable=False)  # ✅ renamed (kg, bags, etc.)
    costPerUnit = Column(Float, nullable=False)
    totalAmount = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False)

    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # relationships
    farmer = relationship("User", back_populates="feeds")
    batch = relationship("Batch", back_populates="feeds")
    unit = relationship("Unit", back_populates="feeds")


class Income(Base):
    __tablename__ = "incomes"

    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    farmerId = Column(Integer, ForeignKey("users.id"), nullable=False)
    batchId = Column(String(50), ForeignKey("batches.batchId"), nullable=False)
    unitId = Column(String(50), ForeignKey("units.id"), nullable=False)
    farmId = Column(Integer, ForeignKey("farms.id"), nullable=False)

    incomeType    = Column(String(250), nullable=False)
    amountEarned= Column(Integer, nullable=False)
    quantitySold = Column(Integer, nullable=False)
    paymentMethod =  Column(String(250), nullable=False)
    incomeDate = Column(DateTime, default=datetime.utcnow)
    # Optional link to harvest (future-proof)
    harvestId = Column(String(50), ForeignKey("harvests.recordId"), nullable=True)
    appliedToPondName = Column(String(100), nullable=True)  # ✅ pond name (unit/pond applied to)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    # farmer = relationship("User", back_populates="incomes")
    # ✅ Relationships

    farmer = relationship("User", back_populates="incomes")
    farm = relationship("Farm", back_populates="incomes")
    batch = relationship("Batch", back_populates="incomes")
    unit = relationship("Unit", back_populates="incomes")

    # farmer = relationship("User", backref="incomes")
    # batch = relationship("Batch", backref="incomes")
    # unit = relationship("Unit", backref="incomes")
    # harvest = relationship("HarvestForm", backref="incomes", uselist=False)


class Stocking(Base):
    __tablename__ = "stockings"

    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    farmerId = Column(Integer, ForeignKey("users.id"), nullable=False)
    batchId = Column(String(50), ForeignKey("batches.batchId"), nullable=False)
    unitId = Column(String(50), ForeignKey("units.id"), nullable=False)
    farmId = Column(Integer, ForeignKey("farms.id"), nullable=False)

    fishType = Column(String(100), nullable=False)            # e.g., Tilapia
    quantityPurchased = Column(Integer, nullable=False)       # total fingerlings stocked
    totalAmount = Column(Float, nullable=False)               # purchase cost
    date = Column(DateTime, default=datetime.utcnow)          # stocking date

    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    farmer = relationship("User", back_populates="stockings")
    farm = relationship("Farm", back_populates="stockings")
    batch = relationship("Batch", back_populates="stockings")
    unit = relationship("Unit", back_populates="stockings")





class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(250), nullable=False)
    description = Column(String(250), nullable=True)
    image = Column(String(250), nullable=True)
    price = Column(Float, nullable=False)
    category = Column(String(250), nullable=False)

    # relationships

    price_range = relationship("PriceRange", uselist=False,  back_populates="product")
    types = relationship("ProductType", back_populates="product", cascade="all, delete-orphan")

# class Category(Base):
#     __tablename__ = "categories"
#     id = Column(Integer, primary_key=True, index=True, autoincrement=True)
#     name = Column(String(250), unique=True, nullable=False)
#
#     # Relationship back to products
#     products = relationship("Product", back_populates="category_obj")

class PriceRange(Base):
    __tablename__ = "price_ranges"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    from_ = Column("from", Float, nullable=False)
    to = Column(Float, nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"))
    product = relationship("Product", back_populates="price_range")


class ProductType(Base):
    __tablename__ = "product_types"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    typeValue = Column(String(230), nullable=False)
    valueMeasurement = Column(String(250), nullable=False)
    valuePrice = Column(Float, nullable=False)
    quantity = Column(Integer, default=0)
    product_id = Column(Integer, ForeignKey("products.id"))
    product = relationship("Product", back_populates="types")

class Cart(Base):
    __tablename__ = "cart"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, nullable=False)

    product = relationship("Product")









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