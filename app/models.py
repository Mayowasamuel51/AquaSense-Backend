from numbers import Integral

from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Numeric, Date, Text, Float, \
    UniqueConstraint, SmallInteger
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


    # incomes = relationship("Income", back_populates="farmer", cascade="all, delete-orphan")

    # links to User

class JustData(Base):
    __tablename__ = "justdata"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    display_name = Column(String(250), nullable=True)
    # relationship back to User
    user = relationship("User", back_populates="justdata")


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    address = Column(String(255), nullable=True)
    longitude = Column(String(100), nullable=True)
    latitude = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    area = Column(String(100), nullable=True)

    # one-to-one with User
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="location")

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
    # ✅ This is the correct place for the owner link
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # ✅ Back relationship to User
    owner = relationship("User", back_populates="farm")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(50), nullable=True)
    user_cluster_name = Column(String(50), nullable=True)
    profilepicture = Column(String(255), nullable=True)
    nin = Column(String(50), nullable=True)
    kyc_status = Column(String(50), default="unverified")
    emailverified = Column(Boolean, default=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    gender = Column(String(50), nullable=True)
    coins = Column(Integer, default=0)
    password_hash = Column(String(255), nullable=False)

    # ✅ One user can have many farms
    farm = relationship("Farm", back_populates="owner", uselist=False)
    # farms = relationship("Farm", back_populates="owner", cascade="all, delete-orphan")

    # ✅ The rest of your relationships stay untouched
    justdata = relationship("JustData", back_populates="user", uselist=False)
    workers = relationship("Worker", back_populates="user")
    tokens = relationship("VerificationToken", back_populates="user")
    video_progress = relationship("UserVideoProgress", backref="user", cascade="all, delete-orphan")
    test_progress = relationship("UserTestProgress", back_populates="user", cascade="all, delete-orphan")
    location = relationship("Location", uselist=False, back_populates="user")
    support_tickets = relationship("SupportAgent", back_populates="user", cascade="all, delete-orphan")
    support_ticket = relationship("SupportTicket", back_populates="user", cascade="all, delete-orphan")
    labs = relationship("Labs", back_populates="user", cascade="all, delete-orphan")
    vetsupports = relationship("VetSupport", back_populates="user", cascade="all, delete-orphan")
    addresses = relationship("DeliveryAddress", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user")
    units = relationship("Unit", back_populates="farmer", cascade="all, delete-orphan")
    batches = relationship("Batch", back_populates="farmer", cascade="all, delete-orphan")
    records = relationship("UnitRecord", back_populates="farmer", cascade="all, delete-orphan")
    feeds = relationship("Feed", back_populates="farmer", cascade="all, delete-orphan")
    incomes = relationship("Income", back_populates="farmer", cascade="all, delete-orphan")
    stockings = relationship("Stocking", back_populates="farmer", cascade="all, delete-orphan")

#
# class BatchInsight(Base):
#     __tablename__ = "batch_insights"
#     id = Column(Integer, primary_key=True)
#     batch_id = Column(String(100), index=True)
#     date = Column(Date)
#     month = Column(Integer)
#     month_name = Column(String(100))
#     population_start = Column(Integer)
#     population_end = Column(Integer)
#     recorded_mortality_no = Column(Integer)
#     recorded_mortality_percent = Column(Float)
#     harvest_no = Column(Integer)
#     abw_start_g = Column(Float)
#     abw_end_g = Column(Float)
#     growth_rate_g_per_day = Column(Float)
#     sgr_percent = Column(Float)
#     adg_g = Column(Float)
#     biomass_start_kg = Column(Float)
#     biomass_end_kg = Column(Float)
#     growth_kg = Column(Float)
#     accumulated_growth_kg = Column(Float)
#     feed_recorded_kg = Column(Float)
#     accumulated_feed_kg = Column(Float)
#     fcr = Column(Float)
#     accumulated_fcr = Column(Float)
class BatchInsight(Base):
    __tablename__ = "batch_insights"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(String(100), index=True)
    date = Column(String(100))

    month = Column(Integer)
    month_name = Column(String(100))

    population_start = Column(Integer)
    population_end = Column(Integer)
    recorded_mortality_no = Column(Integer)
    recorded_mortality_percent = Column(Float)
    harvest_no = Column(Integer)

    abw_start_g = Column(Float)
    abw_end_g = Column(Float)
    growth_rate_g_per_day = Column(Float)
    sgr_percent = Column(Float)
    adg_g = Column(Float)

    biomass_start_kg = Column(Float)
    biomass_end_kg = Column(Float)
    growth_kg = Column(Float)
    accumulated_growth_kg = Column(Float)

    feed_recorded_kg = Column(Float)
    accumulated_feed_kg = Column(Float)
    fcr = Column(Float)
    accumulated_fcr = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)



class Unit(Base):
    __tablename__ = "units"
    id = Column(String(191), primary_key=True, index=True)  # Dart uses String(191) id for Unit
    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    unit_name = Column(String(191), nullable=False)
    unit_type = Column(String(191), nullable=True)
    unit_dimension = Column(String(191), nullable=True)
    unit_capacity = Column(Integer, nullable=True)
    fishes = Column(Integer, nullable=True)
    image_url = Column(String(191), nullable=True)
    image_file = Column(String(191), nullable=True)
    unitcategory = Column(String(191), nullable=True)
    is_active = Column(Integer, default=0)
    is_synced = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)

    farmer = relationship("User", back_populates="units")
    records = relationship("UnitRecord", back_populates="unit", cascade="all, delete-orphan")


class Batch(Base):
    __tablename__ = "batches"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_id = Column(String(36), default=lambda: str(uuid.uuid4()))  # external UUID
    batch_name = Column(String(255), nullable=False)
    is_synced = Column(SmallInteger, nullable=False, default=0)  #
    # fishtype = Column(String(120), nullable=True)
    fishtype = Column(String(120), nullable=True)  # <--- must match DB exactly
    is_completed = Column(SmallInteger, default=0)
    number_of_fishes = Column(Integer, nullable=True)
    age_at_stock = Column(Integer, nullable=True)  # add if you need it
    average_body_weight = Column(Integer, nullable=True)  # optional, match DB
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)
    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    farmer = relationship("User", back_populates="batches")
    records = relationship("UnitRecord", back_populates="batch", cascade="all, delete-orphan")


class UnitRecord(Base):
    __tablename__ = "unit_records"
    id = Column(String(191), primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    batch_id = Column(String(191), ForeignKey("batches.batch_id"), nullable=False)
    unit_id = Column(String(191), ForeignKey("units.id"), nullable=False)
    stocknumber = Column(Integer, nullable=True, default=0)
    fishleft = Column(Integer, nullable=True, default=0)
    mortality = Column(Integer, nullable=True, default=0)
    movedfishes = Column(Integer, nullable=True, default=0)
    incomingfish = Column(Integer, nullable=True, default=0)
    fishtype = Column(String(191), nullable=True)
    stockedon = Column(DateTime, nullable=True)
    totalfishcost = Column(Float, nullable=True)
    is_synced = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)

    farmer = relationship("User", back_populates="records")
    batch = relationship("Batch", back_populates="records")
    unit = relationship("Unit", back_populates="records")

    daily_records = relationship("DailyRecord", back_populates="record", cascade="all, delete-orphan")
    weight_samplings = relationship("WeightSampling", back_populates="record", cascade="all, delete-orphan")
    grading_and_sortings = relationship("GradingAndSorting", back_populates="record", cascade="all, delete-orphan")
    harvests = relationship("HarvestForm", back_populates="record", cascade="all, delete-orphan")


class DailyRecord(Base):
    __tablename__ = "daily_records"
    id = Column(String(191), primary_key=True, index=True)
    record_id = Column(String(191), ForeignKey("unit_records.id"), nullable=False)
    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    batch_id = Column(String(191), ForeignKey("batches.batch_id"), nullable=False)
    unit_id = Column(String(191), ForeignKey("units.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    feed_name = Column(String(191), nullable=True)
    feed_size = Column(String(191), nullable=True)
    feed_quantity = Column(Float, nullable=True)
    mortality = Column(Integer, nullable=True, default=0)
    coins = Column(Float, nullable=True)
    is_synced = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)

    record = relationship("UnitRecord", back_populates="daily_records")


class WeightSampling(Base):
    __tablename__ = "weight_samplings"
    id = Column(String(191), primary_key=True, index=True)
    record_id = Column(String(191), ForeignKey("unit_records.id"), nullable=False)
    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    batch_id = Column(String(191), ForeignKey("batches.batch_id"), nullable=False)
    unit_id = Column(String(191), ForeignKey("units.id"), nullable=False)
    sample_name = Column(String(191), nullable=True)
    date = Column(DateTime, nullable=False)
    fish_numbers = Column(Integer, nullable=False)
    total_weight = Column(Float, nullable=False)
    completed = Column(Integer, nullable=False)
    is_synced = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)
    record = relationship("UnitRecord", back_populates="weight_samplings")


class GradingAndSorting(Base):
    __tablename__ = "grading_and_sortings"
    id = Column(String(191), primary_key=True, index=True)
    record_id = Column(String(191), ForeignKey("unit_records.id"), nullable=False)
    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    batch_id = Column(String(191), ForeignKey("batches.batch_id"), nullable=False)
    unit_id = Column(String(191), ForeignKey("units.id"), nullable=False)
    grade_with = Column(String(191), nullable=True)
    sample_name = Column(String(191), nullable=True)
    date = Column(DateTime, nullable=False)
    grading_pond_number = Column(Integer, nullable=True)
    fish_numbers = Column(Integer, nullable=True)
    total_weight = Column(Float, nullable=True)
    completed = Column(Integer, nullable=False)
    is_synced = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)

    record = relationship("UnitRecord", back_populates="grading_and_sortings")
    grades = relationship("Grade", back_populates="sorting", cascade="all, delete-orphan")


class Grade(Base):
    __tablename__ = "grades"
    id = Column(String(191), primary_key=True, index=True)
    sorting_id = Column(String(191), ForeignKey("grading_and_sortings.id"), nullable=False)
    destination_batch_id = Column(String(191), nullable=True)
    destination_batch_name = Column(String(191), nullable=True)
    destination_unit_id = Column(String(191), nullable=True)
    destination_unit_name = Column(String(191), nullable=True)
    average_fish_weight = Column(Float, nullable=True)
    fish_transferred = Column(Integer, nullable=True)
    sample_name = Column(String(191), nullable=True)
    record_id = Column(String(191), nullable=True)
    batch_id = Column(String(191), nullable=True)
    is_synced = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)

    sorting = relationship("GradingAndSorting", back_populates="grades")


class HarvestForm(Base):
    __tablename__ = "harvests"
    id = Column(String(191), primary_key=True, index=True)
    record_id = Column(String(191), ForeignKey("unit_records.id"), nullable=False)
    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    batch_id = Column(String(191), ForeignKey("batches.batch_id"), nullable=False)
    unit_id = Column(String(191), ForeignKey("units.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    is_synced = Column(Integer, default=0)
    sales_invoice_number = Column(String(191), nullable=True)
    quantity_harvest = Column(Integer, nullable=True)
    total_weight = Column(Float, nullable=True)
    price_per_kg = Column(Float, nullable=True)
    total_sales = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)

    record = relationship("UnitRecord", back_populates="harvests")


# ---------- Example finance/expense models (Income, Stocking, Feed, Labour, Medication etc.) ----------
class Income(Base):
    __tablename__ = "incomes"
    id = Column(String(191), primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("users.id"))
    pond_id = Column(String(191), nullable=True)
    batch_id = Column(String(191), nullable=True)
    income_type = Column(String(191), nullable=True)
    amount_earned = Column(Float, nullable=True)
    amount = Column(Float, nullable=True)
    quantity_sold = Column(Integer, nullable=True)
    payment_method = Column(String(191), nullable=True)
    income_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)
    is_synced = Column(Integer, default=0)
    farmer = relationship("User", back_populates="incomes")


class Stocking(Base):
    __tablename__ = "stockings"
    id = Column(String(191), primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("users.id"))
    pond_id = Column(String(191), nullable=True)
    batch_id = Column(String(191), nullable=True)
    fish_type = Column(String(191), nullable=True)
    quantity_purchased = Column(Integer, nullable=True)
    total_amount = Column(Float, nullable=True)
    date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)
    is_synced = Column(Integer, default=0)

    farmer = relationship("User", back_populates="stockings")


class Feed(Base):
    __tablename__ = "feeds"
    id = Column(String(191), primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("users.id"))
    pond_id = Column(String(191), nullable=True)
    batch_id = Column(String(191), nullable=True)
    feed_name = Column(String(191), nullable=True)
    feed_form = Column(String(191), nullable=True)
    feed_size = Column(String(191), nullable=True)
    quantity = Column(Integer, nullable=True)
    unit = Column(String(191), nullable=True)
    cost_per_unit = Column(Float, nullable=True)
    total_amount = Column(Float, nullable=True)
    date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)
    is_synced = Column(Integer, default=0)

    farmer = relationship("User", back_populates="feeds")


# Additional expense models (Labour, Medication, Maintenance, Logistics, OperationalExpense)
class Labour(Base):
    __tablename__ = "labours"
    id = Column(String(191), primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("users.id"))
    pond_id = Column(String(191), nullable=True)
    batch_id = Column(String(191), nullable=True)
    labour_type = Column(String(191), nullable=True)
    number_of_workers = Column(Integer, nullable=True)
    total_amount = Column(Float, nullable=True)
    date = Column(DateTime, nullable=True)
    payment_method = Column(String(191), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)
    is_synced = Column(Integer, default=0)


class Medication(Base):
    __tablename__ = "medications"
    id = Column(String(191), primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("users.id"))
    pond_id = Column(String(191), nullable=True)
    batch_id = Column(String(191), nullable=True)
    medication_name = Column(String(191), nullable=True)
    quantity = Column(String(191), nullable=True)
    total_cost = Column(Float, nullable=True)
    date_paid = Column(DateTime, nullable=True)
    payment_method = Column(String(191), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)
    is_synced = Column(Integer, default=0)


class Maintenance(Base):
    __tablename__ = "maintenances"
    id = Column(String(191), primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("users.id"))
    pond_id = Column(String(191), nullable=True)
    batch_id = Column(String(191), nullable=True)
    activity_type = Column(String(191), nullable=True)
    total_cost = Column(Float, nullable=True)
    date_paid = Column(DateTime, nullable=True)
    payment_method = Column(String(191), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)
    is_synced = Column(Integer, default=0)


class Logistics(Base):
    __tablename__ = "logistics"
    id = Column(String(191), primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("users.id"))
    pond_id = Column(String(191), nullable=True)
    batch_id = Column(String(191), nullable=True)
    activity_type = Column(String(191), nullable=True)
    total_cost = Column(Float, nullable=True)
    date_paid = Column(DateTime, nullable=True)
    payment_method = Column(String(191), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)
    is_synced = Column(Integer, default=0)


class OperationalExpense(Base):
    __tablename__ = "operational_expenses"
    id = Column(String(191), primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("users.id"))
    pond_id = Column(String(191), nullable=True)
    batch_id = Column(String(191), nullable=True)
    expense_name = Column(String(191), nullable=True)
    total_cost = Column(Float, nullable=True)
    date_paid = Column(DateTime, nullable=True)
    payment_method = Column(String(191), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)
    is_synced = Column(Integer, default=0)


class ProductionMetric(Base):
    __tablename__ = "production_metrics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farmer_id = Column(Integer, nullable=False, index=True)
    batch_id = Column(String(36), nullable=True, index=True)
    unit_id = Column(String(36), nullable=True, index=True)
    production_cycle = Column(Integer, nullable=True)

    # raw inputs
    pond_area_m2 = Column(Float, nullable=True)
    number_stocked = Column(Integer, nullable=True)
    number_harvested = Column(Integer, nullable=True)
    initial_total_biomass_kg = Column(Float, nullable=True)
    final_total_biomass_kg = Column(Float, nullable=True)
    total_feed_given_kg = Column(Float, nullable=True)
    total_feed_cost = Column(Float, nullable=True)

    # computed fields
    yield_kg_m2 = Column(Float, nullable=True)
    yield_kg_cycle = Column(Float, nullable=True)
    survival_rate_pct = Column(Float, nullable=True)
    mortality_rate_pct = Column(Float, nullable=True)
    ADG_g_day = Column(Float, nullable=True)
    SGR_pct_day = Column(Float, nullable=True)
    FCR = Column(Float, nullable=True)
    total_weight_gain_kg = Column(Float, nullable=True)
    feed_cost_per_kg_produced = Column(Float, nullable=True)
    stocking_density_fish_m2 = Column(Float, nullable=True)
    total_cost = Column(Float, nullable=True)
    cost_per_kg = Column(Float, nullable=True)
    total_revenue = Column(Float, nullable=True)
    gross_profit = Column(Float, nullable=True)
    profit_per_kg = Column(Float, nullable=True)
    gross_margin_pct = Column(Float, nullable=True)
    ROI_pct = Column(Float, nullable=True)

    computed_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("farmer_id", "batch_id", "unit_id", "production_cycle", name="uq_prodmetric_fbuc"),
    )
#
# class SyncBase:
#     # client-provided UUID primary key
#     id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
#     farmer_id = Column(Integer, nullable=False, index=True)
#     created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)
#     is_synced = Column(Boolean, default=False, nullable=False)
#
#
# # ---------------------
# # Unit (pond/cage)
# # ---------------------
# class Unit(Base, SyncBase):
#     __tablename__ = "units"
#
#     unit_name = Column(String(120), nullable=False)
#     unit_type = Column(String(80), nullable=True)
#     unit_dimension = Column(String(120), nullable=True)
#     unit_capacity = Column(Integer, nullable=True)
#     fishes = Column(Integer, default=0)
#     image_url = Column(String(255), nullable=True)
#     image_file = Column(String(255), nullable=True)
#     unit_category = Column(String(80), nullable=True)  # cage / pond
#     is_active = Column(Boolean, default=False)
#     # ✅ This line is critical
#     farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     # relationships
#     farmer = relationship("User", back_populates="units")
#     # reverse relationships from other models will reference Unit via pond_id/unit_id
#
#
# # ---------------------
# # Batch
# # ---------------------
# class Batch(Base, SyncBase):
#     __tablename__ = "batches"
#
#     batch_name = Column(String(255), nullable=False)
#     fishtype = Column(String(120), nullable=True)
#     is_completed = Column(Boolean, default=False)
#     number_of_fishes = Column(Integer, default=0)
#     # ✅ This line is critical
#     farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#
#     farmer = relationship("User", back_populates="batches")
#
#
# # ---------------------
# # UnitRecord (per unit per batch)
# # ---------------------
# class UnitRecord(Base, SyncBase):
#     __tablename__ = "unit_records"
#
#     # SyncBase provides: id, farmer_id, created_at, updated_at, is_synced
#     batch_id = Column(String(36), ForeignKey("batches.id"), nullable=False, index=True)
#     unit_id = Column(String(36), ForeignKey("units.id"), nullable=False, index=True)
#     fishleft = Column(Integer, default=0)
#     stocknumber = Column(Integer, default=0)
#     incomingfish = Column(Integer, default=0)
#     mortality = Column(Integer, default=0)
#     movedfishes = Column(Integer, default=0)
#     fishtype = Column(String(100), nullable=True)
#     stockedon = Column(DateTime, nullable=True)
#     totalfishcost = Column(Float, nullable=True)
#     # ✅ Add this line:
#     farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#
#     farmer = relationship("User", back_populates="records")
#     batch = relationship("Batch", backref="unit_records")
#     unit = relationship("Unit", backref="unit_records")
#
#
# # ---------------------
# # DailyRecord
# # ---------------------
# class DailyRecord(Base, SyncBase):
#     __tablename__ = "daily_records"
#
#     record_id = Column(String(36), ForeignKey("unit_records.id"), nullable=False, index=True)
#     batch_id = Column(String(36), ForeignKey("batches.id"), nullable=False, index=True)
#     unit_id = Column(String(36), ForeignKey("units.id"), nullable=False, index=True)
#     date = Column(DateTime, nullable=False)
#     feed_name = Column(String(120), nullable=True)
#     feed_size = Column(String(80), nullable=True)
#     feed_quantity = Column(Float, nullable=False, default=0.0)
#     mortality = Column(Integer, default=0)
#     coins = Column(Float, nullable=True)
#     # ✅ This line is critical
#     farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     farmer = relationship("User")
#     unit_record = relationship("UnitRecord", backref="daily_records")
#
#
# # ---------------------
# # WeightSampling
# # ---------------------
# class WeightSampling(Base, SyncBase):
#     __tablename__ = "weight_samplings"
#
#     record_id = Column(String(36), ForeignKey("unit_records.id"), nullable=False)
#     batch_id = Column(String(36), ForeignKey("batches.id"), nullable=False)
#     unit_id = Column(String(36), ForeignKey("units.id"), nullable=False)
#     sample_name = Column(String(120), nullable=True)
#     date = Column(DateTime, nullable=False)
#     fish_numbers = Column(Integer, nullable=False)
#     total_weight = Column(Float, nullable=False)
#     completed = Column(Boolean, default=False)
#     farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     farmer = relationship("User")
#     unit_record = relationship("UnitRecord", backref="weight_samplings")
#
#
# # ---------------------
# # Grading & Sorting
# # ---------------------
# class GradingAndSorting(Base, SyncBase):
#     __tablename__ = "grading_sortings"
#
#     record_id = Column(String(36), ForeignKey("unit_records.id"), nullable=False)
#     batch_id = Column(String(36), ForeignKey("batches.id"), nullable=False)
#     unit_id = Column(String(36), ForeignKey("units.id"), nullable=False)
#     grade_with = Column(String(120), nullable=True)
#     sample_name = Column(String(120), nullable=True)
#     date = Column(DateTime, nullable=False)
#     grading_pond_number = Column(Integer, nullable=True)
#     fish_numbers = Column(Integer, nullable=True)
#     total_weight = Column(Float, nullable=True)
#     completed = Column(Boolean, default=False)
#     farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     farmer = relationship("User")
#     unit_record = relationship("UnitRecord", backref="grading_sortings")
#     grades = relationship("Grade", back_populates="grading", cascade="all, delete-orphan")
#
#
# class Grade(Base):
#     __tablename__ = "grades"
#
#     id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
#     sorting_id = Column(String(36), ForeignKey("grading_sortings.id"), nullable=False, index=True)
#     destination_batch_id = Column(String(36), nullable=True)
#     destination_batch_name = Column(String(255), nullable=True)
#     destination_unit_id = Column(String(36), nullable=True)
#     destination_unit_name = Column(String(255), nullable=True)
#     average_fish_weight = Column(Float, nullable=True)
#     fish_transferred = Column(Integer, nullable=True)
#     sample_name = Column(String(120), nullable=True)
#     record_id = Column(String(36), nullable=True)
#     batch_id = Column(String(36), nullable=True)
#     is_synced = Column(Boolean, default=False)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
#
#     grading = relationship("GradingAndSorting", back_populates="grades")
#
#
# # ---------------------
# # Harvest
# # ---------------------
# class Harvest(Base, SyncBase):
#     __tablename__ = "harvests"
#
#     record_id = Column(String(36), ForeignKey("unit_records.id"), nullable=False)
#     batch_id = Column(String(36), ForeignKey("batches.id"), nullable=False)
#     unit_id = Column(String(36), ForeignKey("units.id"), nullable=False)
#     date = Column(DateTime, nullable=False)
#     sales_invoice_number = Column(String(120), nullable=True)
#     quantity_harvest = Column(Integer, nullable=False, default=0)
#     total_weight = Column(Float, nullable=False, default=0.0)
#     price_per_kg = Column(Float, nullable=True)
#     total_sales = Column(Float, nullable=True)
#     farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     farmer = relationship("User")
#     unit_record = relationship("UnitRecord", backref="harvests")
#
#
# # ---------------------
# # Financial / Expense models
# # ---------------------
# class Income(Base, SyncBase):
#     __tablename__ = "incomes"
#
#     title = Column(String(120), default="Income")
#     content = Column(Text, nullable=True)
#     icon = Column(String(255), nullable=True)
#     pond_id = Column(String(36), ForeignKey("units.id"), nullable=True)
#     batch_id = Column(String(36), ForeignKey("batches.id"), nullable=True)
#     income_type = Column(String(120), nullable=True)
#     amount_earned = Column(Float, nullable=True)
#     amount = Column(Float, nullable=False, default=0.0)
#     quantity_sold = Column(Integer, nullable=True)
#     payment_method = Column(String(80), nullable=True)
#     income_date = Column(DateTime, nullable=True)
#     farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     farmer = relationship("User")
#     pond = relationship("Unit")
#
#
# class Stocking(Base, SyncBase):
#     __tablename__ = "stockings"
#
#     title = Column(String(120), default="Stocking")
#     content = Column(Text, nullable=True)
#     icon = Column(String(255), nullable=True)
#     pond_id = Column(String(36), ForeignKey("units.id"), nullable=True)
#     batch_id = Column(String(36), ForeignKey("batches.id"), nullable=True)
#     fish_type = Column(String(120), nullable=True)
#     quantity_purchased = Column(Integer, nullable=False, default=0)
#     total_amount = Column(Float, nullable=True)
#     date = Column(DateTime, nullable=True)
#     farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     farmer = relationship("User")
#     pond = relationship("Unit")
#
#
# class Feed(Base, SyncBase):
#     __tablename__ = "feeds"
#
#     title = Column(String(120), default="Feed")
#     content = Column(Text, nullable=True)
#     icon = Column(String(255), nullable=True)
#     amount = Column(Float, nullable=True)
#     pond_id = Column(String(36), ForeignKey("units.id"), nullable=True)
#     batch_id = Column(String(36), ForeignKey("batches.id"), nullable=True)
#     feed_name = Column(String(120), nullable=True)
#     feed_form = Column(String(100), nullable=True)
#     feed_size = Column(String(80), nullable=True)
#     quantity = Column(Integer, nullable=True)
#     unit = Column(String(50), nullable=True)
#     cost_per_unit = Column(Float, nullable=True)
#     total_amount = Column(Float, nullable=True)
#     date = Column(DateTime, nullable=True)
#     farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     farmer = relationship("User")
#     pond = relationship("Unit")
#     batch = relationship("Batch")
#
#
# class Labour(Base, SyncBase):
#     __tablename__ = "labours"
#
#     title = Column(String(120), default="Salary/wages")
#     content = Column(Text, nullable=True)
#     icon = Column(String(255), nullable=True)
#     amount = Column(Float, nullable=True)
#     pond_id = Column(String(36), ForeignKey("units.id"), nullable=True)
#     batch_id = Column(String(36), ForeignKey("batches.id"), nullable=True)
#     labour_type = Column(String(120), nullable=True)
#     number_of_workers = Column(Integer, nullable=True)
#     total_amount = Column(Float, nullable=True)
#     payment_method = Column(String(80), nullable=True)
#     date = Column(DateTime, nullable=True)
#     notes = Column(Text, nullable=True)
#     farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     farmer = relationship("User")
#     pond = relationship("Unit")
#
#
# class Medication(Base, SyncBase):
#     __tablename__ = "medications"
#
#     title = Column(String(120), default="Medications")
#     content = Column(Text, nullable=True)
#     icon = Column(String(255), nullable=True)
#     amount = Column(Float, nullable=True)
#     pond_id = Column(String(36), ForeignKey("units.id"), nullable=True)
#     batch_id = Column(String(36), ForeignKey("batches.id"), nullable=True)
#     medication_name = Column(String(120), nullable=True)
#     quantity = Column(String(120), nullable=True)
#     total_cost = Column(Float, nullable=True)
#     date_paid = Column(DateTime, nullable=True)
#     payment_method = Column(String(80), nullable=True)
#     notes = Column(Text, nullable=True)
#     farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     farmer = relationship("User")
#     pond = relationship("Unit")
#
#
# class Maintenance(Base, SyncBase):
#     __tablename__ = "maintenances"
#
#     title = Column(String(120), default="Farm Maintenance")
#     content = Column(Text, nullable=True)
#     icon = Column(String(255), nullable=True)
#     amount = Column(Float, nullable=True)
#     pond_id = Column(String(36), ForeignKey("units.id"), nullable=True)
#     batch_id = Column(String(36), ForeignKey("batches.id"), nullable=True)
#     activity_type = Column(String(120), nullable=True)
#     total_cost = Column(Float, nullable=True)
#     date_paid = Column(DateTime, nullable=True)
#     payment_method = Column(String(80), nullable=True)
#     notes = Column(Text, nullable=True)
#     farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     farmer = relationship("User")
#     pond = relationship("Unit")
#
#
# class Logistics(Base, SyncBase):
#     __tablename__ = "logistics"
#
#     title = Column(String(120), default="Logistics")
#     content = Column(Text, nullable=True)
#     icon = Column(String(255), nullable=True)
#     amount = Column(Float, nullable=True)
#     pond_id = Column(String(36), ForeignKey("units.id"), nullable=True)
#     batch_id = Column(String(36), ForeignKey("batches.id"), nullable=True)
#     activity_type = Column(String(120), nullable=True)
#     total_cost = Column(Float, nullable=True)
#     date_paid = Column(DateTime, nullable=True)
#     payment_method = Column(String(80), nullable=True)
#     notes = Column(Text, nullable=True)
#     farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     farmer = relationship("User")
#     pond = relationship("Unit")
#
#
# class OperationalExpense(Base, SyncBase):
#     __tablename__ = "operational_expenses"
#
#     title = Column(String(120), default="Other Operations")
#     content = Column(Text, nullable=True)
#     icon = Column(String(255), nullable=True)
#     amount = Column(Float, nullable=True)
#     pond_id = Column(String(36), ForeignKey("units.id"), nullable=True)
#     batch_id = Column(String(36), ForeignKey("batches.id"), nullable=True)
#     expense_name = Column(String(120), nullable=True)
#     total_cost = Column(Float, nullable=True)
#     date_paid = Column(DateTime, nullable=True)
#     payment_method = Column(String(80), nullable=True)
#     notes = Column(Text, nullable=True)
#     farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     farmer = relationship("User")
#     pond = relationship("Unit")
#
#
# # ---------------------
# # Production Metrics (computed & stored)
# # ---------------------
# class ProductionMetric(Base):
#     __tablename__ = "production_metrics"
#
#     id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
#     farmer_id = Column(Integer, nullable=False, index=True)
#     batch_id = Column(String(36), nullable=True, index=True)
#     unit_id = Column(String(36), nullable=True, index=True)
#     production_cycle = Column(Integer, nullable=True)
#
#     # raw inputs
#     pond_area_m2 = Column(Float, nullable=True)
#     number_stocked = Column(Integer, nullable=True)
#     number_harvested = Column(Integer, nullable=True)
#     initial_total_biomass_kg = Column(Float, nullable=True)
#     final_total_biomass_kg = Column(Float, nullable=True)
#     total_feed_given_kg = Column(Float, nullable=True)
#     total_feed_cost = Column(Float, nullable=True)
#
#     # computed fields
#     yield_kg_m2 = Column(Float, nullable=True)
#     yield_kg_cycle = Column(Float, nullable=True)
#     survival_rate_pct = Column(Float, nullable=True)
#     mortality_rate_pct = Column(Float, nullable=True)
#     ADG_g_day = Column(Float, nullable=True)
#     SGR_pct_day = Column(Float, nullable=True)
#     FCR = Column(Float, nullable=True)
#     total_weight_gain_kg = Column(Float, nullable=True)
#     feed_cost_per_kg_produced = Column(Float, nullable=True)
#     stocking_density_fish_m2 = Column(Float, nullable=True)
#     total_cost = Column(Float, nullable=True)
#     cost_per_kg = Column(Float, nullable=True)
#     total_revenue = Column(Float, nullable=True)
#     gross_profit = Column(Float, nullable=True)
#     profit_per_kg = Column(Float, nullable=True)
#     gross_margin_pct = Column(Float, nullable=True)
#     ROI_pct = Column(Float, nullable=True)
#
#     computed_at = Column(DateTime, default=datetime.utcnow)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
#
#     __table_args__ = (
#         UniqueConstraint("farmer_id", "batch_id", "unit_id", "production_cycle", name="uq_prodmetric_fbuc"),
#     )
#





class Cluster(Base):
    __tablename__ = "clusters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    location = Column(String(100), nullable=False)
    farmer_count = Column(Integer, default=0)

    # Relationship to members
    farmers = relationship("ClusterFarmer", back_populates="cluster", cascade="all, delete-orphan")

class ClusterFarmer(Base):
    __tablename__ = "cluster_farmers"

    id = Column(Integer, primary_key=True, index=True)
    cluster_id = Column(Integer, ForeignKey("clusters.id"))
    farmer_name = Column(String(100), nullable=False)
    farmer_email = Column(String(255), nullable=False)

    cluster = relationship("Cluster", back_populates="farmers")

    __table_args__ = (
        UniqueConstraint('cluster_id', 'farmer_email', name='uq_cluster_farmer'),
    )
# class Cluster(Base):
#     __tablename__ = "clusters"
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(100), nullable=False)  # e.g. "Ikeja Cluster 1"
#     location = Column(String(100), nullable=False)
#     farmer_count = Column(Integer, default=0)
#     # relationship
#     # farmers = relationship("User", back_populates="cluster")

class Vendor(Base):
    __tablename__ = "vendor"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(50), nullable=True)
    profilepicture = Column(String(255), nullable=True)
    kyc_status = Column(String(50), default="unverified")
    emailverified = Column(Boolean, default=False)
    first_name = Column(String(100), nullable=True)
    description  = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    gender = Column(String(50), nullable=True)
    password_hash = Column(String(255), nullable=False)

    # New address/location fields
    address = Column(String(255), nullable=True)
    longitude = Column(String(100), nullable=True)
    latitude = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    area = Column(String(100), nullable=True)
    pick_up_station_address  = Column(String(100), nullable=True , default="Aquasense pickup station 1 Montgomery Road Ikeja, Lagos")
    opening_hour = Column(String(200), nullable=True , default="Monday - Friday 8 AM - 6 PM; Saturday 9 AM - 6 PM")
    # relationship to tokens
    tokens = relationship("VerificationToken", back_populates="vendor")
    products = relationship("Product", back_populates="vendor", cascade="all, delete-orphan")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    image = Column(String(255), nullable=True)
    price = Column(Float, nullable=False)
    category = Column(String(100), nullable=False)
    price_from = Column(Float, nullable=True)
    price_to = Column(Float, nullable=True)
    # New fields ↓↓↓
    featured = Column(Boolean, default=False)
    featured_expiry_date = Column(DateTime, nullable=True)
    discount_percent = Column(Float, nullable=True, default=0.0)
    discount_amount = Column(Float, nullable=True, default=0.0)
    vendor_id = Column(Integer, ForeignKey("vendor.id"))  # link to vendor
    vendor = relationship("Vendor", back_populates="products")
    types = relationship("ProductType", back_populates="product", cascade="all, delete-orphan")

class ProductType(Base):
    __tablename__ = "product_types"
    id = Column(Integer, primary_key=True, index=True)
    type_value = Column(String(255), nullable=False)
    value_measurement = Column(String(100), nullable=True)
    value_size = Column(String(100), nullable=True)
    value_price = Column(Float, nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"))
    product = relationship("Product", back_populates="types")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_amount = Column(Float, nullable=False)
    status = Column(String(50), default="pending")
    payment_reference = Column(String(255), unique=True, index=True, nullable=True)
    # payment_reference = Column(String(255), unique=True, nullable=True)
    payment_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    delivery_address_id = Column(Integer, ForeignKey("delivery_addresses.id"), nullable=True)
    delivery_address = relationship("DeliveryAddress")
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete")

class DeliveryAddress(Base):
    __tablename__ = "delivery_addresses"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # recipient_name = Column(String(100), nullable=True)
    phone_number = Column(String(50), nullable=True)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    additional_number = Column(String(50), nullable=True)
    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    delivery_address = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    # Relationship
    user = relationship("User", back_populates="addresses")
class WebhookLog(Base):
    __tablename__ = "webhook_logs"
    id = Column(Integer, primary_key=True)
    event = Column(String(100))
    reference = Column(String(100))
    payload = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    vendor_id = Column(Integer, ForeignKey("vendor.id"))  # ✅ fixed here
    type_id = Column(Integer, ForeignKey("product_types.id"))
    quantity = Column(Integer, default=1)
    price = Column(Float, nullable=False)
    discount_price = Column(Float, nullable=True)
    subtotal = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product")
    vendor = relationship("Vendor")
    type = relationship("ProductType")

class VerificationToken(Base):
    __tablename__ = "verification_tokens"
    id = Column(Integer,primary_key=True, index=True, autoincrement=True)
    token = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    vendor_id = Column(Integer, ForeignKey("vendor.id"), nullable=True)
    # expires_at = Column(DateTime, default=lambda: datetime.datetime.utcnow() + datetime.timedelta(hours=2))
    user = relationship("User", back_populates="tokens")
    # relationship back to vendor
    vendor = relationship("Vendor", back_populates="tokens")

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

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_amount = Column(Float, nullable=False)
    coins_used = Column(Integer, default=0)
    discount = Column(Float, default=0)
    final_amount = Column(Float, nullable=False)
    status = Column(String(550), default="pending")  # pending, success, failed
    paystack_ref = Column(String(550), nullable=True, unique=True)
    items_json = Column(JSON, nullable=True)  # 🆕 store cart items


class Labs(Base):
    __tablename__ = "labs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    username = Column(String(250), nullable=False)
    preferred_date = Column(String(250), nullable=False)
    totalPrice = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=True)
    transaction_reference = Column(String(255), nullable=True)
    payment_status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # 🧩 Relationship to lab tests (categories/tests)
    tests = relationship("LabTest", back_populates="lab", cascade="all, delete-orphan")
    # 🧩 Relationship back to User
    user = relationship("User", back_populates="labs")

class LabTest(Base):
    __tablename__ = "lab_tests"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    lab_id = Column(Integer, ForeignKey("labs.id"), nullable=False)
    # ✅ match payload
    category_title = Column(String(255), nullable=False)  # e.g. "Water Quality Test"
    test_id = Column(Integer, nullable=False)  # testListAsMap test id
    test_name = Column(String(255), nullable=False)  # e.g. "pH Level"
    test_price = Column(Float, nullable=False)

    lab = relationship("Labs", back_populates="tests")
class SupportAgent(Base):
    __tablename__ = "supportagent"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    helpwith = Column(String(250), nullable=False)
    issue= Column(String(500), nullable=True)
    date = Column(String(250), nullable=False)
    username = Column(String(250), nullable=False)
    # Link to User table
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="support_tickets")  # optional, for easy access

class VetSupport(Base):
    __tablename__ = "vetsupport"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    helpwith = Column(String(250), nullable=False)
    modeofsupport = Column(String(250), nullable=False)
    issue = Column(String(550), nullable=False)
    image= Column(String(500), nullable=True)
    video = Column(String(500), nullable=True)
    date = Column(String(250), nullable=False)
    username = Column(String(250), nullable=True)
    coins = Column(String(240), nullable=True)
    # ✅ Create foreign key to users table
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    # ✅ Relationship back to User
    user = relationship("User", back_populates="vetsupports")
    images = relationship("VetImage", back_populates="vetsupport", cascade="all, delete-orphan")
    videos = relationship("VetVideo", back_populates="vetsupport", cascade="all, delete-orphan")

class VetVideo(Base):
    __tablename__ = "vetvideos"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    url = Column(String(500), nullable=False)
    vetsupport_id = Column(Integer, ForeignKey("vetsupport.id", ondelete="CASCADE"))
    vetsupport = relationship("VetSupport", back_populates="videos")

class VetImage(Base):
    __tablename__ = "vetimages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    url = Column(String(500), nullable=False)
    vetsupport_id = Column(Integer, ForeignKey("vetsupport.id", ondelete="CASCADE"))

    # ✅ Relationship back to VetSupport
    vetsupport = relationship("VetSupport", back_populates="images")

class SupportTicket(Base):
    __tablename__ = "support_tickets"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category = Column(String(100), nullable=False)  # e.g., "Emergency", "Order", "Bulk Purchase"
    message = Column(String(1000), nullable=True)   # farmer’s message
    response = Column(String(1000), nullable=True)  # admin/expert reply
    status = Column(String(50), default="open")     # open, answered, closed
    farmer_name = Column(String(100), nullable=True)
    # Link to User table
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="support_ticket")  # access the user object


class TestCategory(Base):
    __tablename__ = "test_categories"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), unique=True, nullable=False)

    # Relationship to test_items table
    tests = relationship("TestItem", back_populates="category", cascade="all, delete-orphan")

class TestItem(Base):
    __tablename__ = "test_items"  # 👈 new table name (no conflict)
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    price = Column(Integer, nullable=False)
    category_id = Column(Integer, ForeignKey("test_categories.id"), nullable=False)
    # Link back to category
    category = relationship("TestCategory", back_populates="tests")

class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(512), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_super = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class AdminOTP(Base):
    __tablename__ = "admin_otps"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("admins.id", ondelete="CASCADE"), nullable=True)
    email = Column(String(255), nullable=False, index=True)
    otp_hash = Column(String(512), nullable=False)
    purpose = Column(String(50), default="password_reset")  # e.g., password_reset
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    admin = relationship("Admin", backref="otps")








#
# class User(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True, index=True, autoincrement=True)
#     email = Column(String(255), unique=True, nullable=False)
#     phone = Column(String(50), nullable=True)
#     user_cluster_name = Column(String(50), nullable=True)
#     profilepicture = Column(String(255), nullable=True )
#     nin = Column(String(50), nullable=True)
#     kyc_status = Column(String(50), default="unverified")
#     emailverified = Column(Boolean, default=False)
#     first_name = Column(String(100), nullable=True)
#     last_name = Column(String(100), nullable=True)
#     gender = Column(String(50), nullable=True)
#     coins = Column(Integer, default=0)
#     # ✅ Progress relationships
#     justdata = relationship("JustData", back_populates="user", uselist=False)
#     password_hash = Column(String(255), nullable=False)
#     # roles = Column(JSON, default=["user"])  # stored as JSON array in MySQL
#     # farm = relationship("Farm", uselist=False, backref="owner")
#     workers = relationship("Worker", back_populates="user")
#     # relationship to tokens
#     tokens = relationship("VerificationToken", back_populates="user")
#     # ✅ relationships
#     video_progress = relationship("UserVideoProgress", backref="user", cascade="all, delete-orphan")
#     test_progress = relationship("UserTestProgress", back_populates="user", cascade="all, delete-orphan")
#     # new relationship
#     location = relationship("Location", uselist=False, back_populates="user")
#     # ✅ add this only once
#     # incomes = relationship("Income", back_populates="farmer")
#     support_tickets = relationship("SupportAgent", back_populates="user", cascade="all, delete-orphan")
#     # Reverse relationship to support tickets
#     support_ticket = relationship("SupportTicket", back_populates="user", cascade="all, delete-orphan")
#     # 🧩 Add this line:
#     labs = relationship("Labs", back_populates="user",  cascade="all, delete-orphan")
#     # ✅ Add relationship to VetSupport
#     vetsupports = relationship("VetSupport", back_populates="user", cascade="all, delete-orphan")
#     addresses = relationship("DeliveryAddress", back_populates="user", cascade="all, delete-orphan")
#     # ✅ Relationship to Orders
#     orders = relationship("Order", back_populates="user")
#     owner_id = Column(Integer, ForeignKey("users.id"), unique=True)
#
#     owner = relationship("User", back_populates="farms")  # ✅ Matches
#     # cluster_id = Column(Integer, ForeignKey("clusters.id"), nullable=True)  // i will fix  this God abeg
#     # cluster = relationship("Cluster", back_populates="farmers")  // and this too
#     # relationships to farm data
#     units = relationship("Unit", back_populates="farmer", cascade="all, delete-orphan")
#     batches = relationship("Batch", back_populates="farmer", cascade="all, delete-orphan")
#     records = relationship("UnitRecord", back_populates="farmer", cascade="all, delete-orphan")
#     feeds = relationship("Feed", back_populates="farmer", cascade="all, delete-orphan")
#     incomes = relationship("Income", back_populates="farmer", cascade="all, delete-orphan")
#     stockings = relationship("Stocking", back_populates="farmer", cascade="all, delete-orphan")






# class Unit(Base):
#     __tablename__ = "units"
#
#     id = Column(String(50), primary_key=True, index=True)
#     farmerId = Column(Integer, ForeignKey("users.id"), nullable=False)
#     pondName = Column(String(100), nullable=False)
#     pondType = Column(String(50), nullable=False)  # e.g., Earthen, Concrete
#     pondCapacity = Column(Integer, nullable=False)
#     fishes = Column(Integer, nullable=False)
#     imageUrl = Column(String(255))
#     createdAt = Column(DateTime, default=datetime.utcnow)
#     updatedAt = Column(DateTime, default=None)
#     type = Column(String(50))  # e.g., "Cage" or "Pond"
#     isActive = Column(Boolean, default=False)
#     # ✅ Add feeds relationship
#     feeds = relationship("Feed", back_populates="unit")
#     farmer = relationship("User", back_populates="units")
#     records = relationship("Record", back_populates="unit")
#     # Unit model
#
#     incomes = relationship("Income", back_populates="unit")
#     # In Unit
#     stockings = relationship("Stocking", back_populates="unit")
#
#
# class Batch(Base):
#     __tablename__ = "batches"
#     batchId = Column(String(50), primary_key=True, index=True)
#     farmerId = Column(Integer, ForeignKey("users.id"), nullable=False)
#     batchName = Column(String(100), nullable=False)
#     fishtype = Column(String(100), nullable=False)
#     numberoffishes = Column(String(100), nullable=False)
#     createdAt = Column(DateTime, default=datetime.utcnow)
#     updatedAt = Column(DateTime, default=None)
#     isCompleted = Column(Boolean, default=False)
#     farmer = relationship("User", back_populates="batches")
#     records = relationship("Record", back_populates="batch")
#     # ✅ Add feeds relationship
#     feeds = relationship("Feed", back_populates="batch")
#     # Batch model
#
#     incomes = relationship("Income", back_populates="batch")   # ✅ matches Income.batch
#     # In Batch
#     stockings = relationship("Stocking", back_populates="batch")

#
# class Record(Base):
#     __tablename__ = "records"
#
#     id = Column(String(50), primary_key=True, index=True)
#     farmerId = Column(Integer, ForeignKey("users.id"), nullable=False)
#     batchId = Column(String(50), ForeignKey("batches.batchId"))
#     unitId = Column(String(50), ForeignKey("units.id"))
#
#     createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)
#     updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
#     unit = relationship("Unit", back_populates="records")
#     batch = relationship("Batch", back_populates="records")
#     farmer = relationship("User", back_populates="records")
#
#     dailyRecords = relationship("DailyRecord", back_populates="record")
#     weightSamplings = relationship("WeightSampling", back_populates="record")
#     gradingAndSortings = relationship("GradingAndSorting", back_populates="record")
#     harvests = relationship("HarvestForm", back_populates="record")
#
# class DailyRecord(Base):
#     __tablename__ = "daily_records"
#
#     id = Column(String(50), primary_key=True, index=True)   # PK UUID
#     recordId = Column(String(50), ForeignKey("records.id")) # FK to records
#     farmerId = Column(Integer, ForeignKey("users.id"), nullable=False)
#     batchId = Column(String(50), ForeignKey("batches.batchId"))
#     unitId = Column(String(50), ForeignKey("units.id"))
#
#     date = Column(DateTime, nullable=False)
#     feedName = Column(String(100), nullable=False)
#     feedSize = Column(String(50), nullable=False)
#     feedQuantity = Column(Float, nullable=False)
#     mortality = Column(Integer, nullable=False)
#     coins = Column(Integer, default=None)
#
#     createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)
#     updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
#
#     # Relationships
#     record = relationship("Record", back_populates="dailyRecords")
#
# class WeightSampling(Base):
#     __tablename__ = "weight_samplings"
#
#     recordId = Column(String(50), ForeignKey("records.id"), primary_key=True)
#     farmerId = Column(Integer, ForeignKey("users.id"), nullable=False)
#     batchId = Column(String(50), ForeignKey("batches.batchId"))
#     unitId = Column(String(50), ForeignKey("units.id"))
#     sampleName = Column(String(100))
#     date = Column(DateTime, nullable=False)
#     fishNumbers = Column(Integer, nullable=False)
#     totalWeight = Column(Float, nullable=False)
#     completed = Column(Boolean, default=False)
#     createdAt = Column(DateTime, default=datetime.utcnow)
#
#     record = relationship("Record", back_populates="weightSamplings")
#
# class Grade(Base):
#     __tablename__ = "grades"
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     gradingAndSortingId = Column(String(50), ForeignKey("grading_and_sortings.recordId"))
#     destinationBatchId = Column(String(50), nullable=True)
#     destinationBatchName = Column(String(100), nullable=True)
#     destinationUnitId = Column(String(50), nullable=False)
#     destinationUnitName = Column(String(100), nullable=False)
#     averageFishWeight = Column(Float, nullable=False)
#     fishTransferred = Column(Integer, nullable=False)
#
# class GradingAndSorting(Base):
#     __tablename__ = "grading_and_sortings"
#
#     recordId = Column(String(50), ForeignKey("records.id"), primary_key=True)
#     farmerId = Column(Integer, ForeignKey("users.id"), nullable=False)
#     batchId = Column(String(50), ForeignKey("batches.batchId"))
#     unitId = Column(String(50), ForeignKey("units.id"))
#     gradeWith = Column(String(50))
#     sampleName = Column(String(100))
#     date = Column(DateTime, nullable=False)
#     gradingPondNumber = Column(Integer)
#     fishNumbers = Column(Integer)
#     totalWeight = Column(Float)
#     completed = Column(Boolean, default=False)
#     createdAt = Column(DateTime, default=datetime.utcnow)
#
#     record = relationship("Record", back_populates="gradingAndSortings")
#     grades = relationship("Grade", backref="gradingAndSorting")
#
# class HarvestForm(Base):
#     __tablename__ = "harvests"
#
#     recordId = Column(String(50), ForeignKey("records.id"), primary_key=True)
#     farmerId = Column(Integer, ForeignKey("users.id"), nullable=False)
#     batchId = Column(String(50), ForeignKey("batches.batchId"))
#     unitId = Column(String(50), ForeignKey("units.id"))
#     date = Column(DateTime, nullable=False)
#     harvestedWeight = Column(Float, nullable=False)
#     harvestedFish = Column(Integer, nullable=False)
#     createdAt = Column(DateTime, default=datetime.utcnow)
#
#     record = relationship("Record", back_populates="harvests")
#
# class Feed(Base):
#     __tablename__ = "feeds"
#
#     id = Column(String(50), primary_key=True, index=True)
#     farmerId = Column(Integer, ForeignKey("users.id"), nullable=False)
#
#     batchId = Column(String(50), ForeignKey("batches.batchId"), nullable=False)
#     unitId = Column(String(50), ForeignKey("units.id"), nullable=False)
#
#     feedName = Column(String(100), nullable=False)
#     feedForm = Column(String(50), nullable=False)
#     feedSize = Column(String(50), nullable=False)
#     quantity = Column(Integer, nullable=False)
#     # unit = Column(String(50), nullable=False)
#     unitMeasure = Column(String(50), nullable=False)  # ✅ renamed (kg, bags, etc.)
#     costPerUnit = Column(Float, nullable=False)
#     totalAmount = Column(Float, nullable=False)
#     date = Column(DateTime, nullable=False)
#
#     createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)
#     updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
#
#     # relationships
#     farmer = relationship("User", back_populates="feeds")
#     batch = relationship("Batch", back_populates="feeds")
#     unit = relationship("Unit", back_populates="feeds")
#
#
# class Income(Base):
#     __tablename__ = "incomes"
#
#     id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
#     farmerId = Column(Integer, ForeignKey("users.id"), nullable=False)
#     batchId = Column(String(50), ForeignKey("batches.batchId"), nullable=False)
#     unitId = Column(String(50), ForeignKey("units.id"), nullable=False)
#     farmId = Column(Integer, ForeignKey("farms.id"), nullable=False)
#
#     incomeType    = Column(String(250), nullable=False)
#     amountEarned= Column(Integer, nullable=False)
#     quantitySold = Column(Integer, nullable=False)
#     paymentMethod =  Column(String(250), nullable=False)
#     incomeDate = Column(DateTime, default=datetime.utcnow)
#     # Optional link to harvest (future-proof)
#     harvestId = Column(String(50), ForeignKey("harvests.recordId"), nullable=True)
#     appliedToPondName = Column(String(100), nullable=True)  # ✅ pond name (unit/pond applied to)
#     createdAt = Column(DateTime, default=datetime.utcnow)
#     updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
#
#     # Relationships
#     # farmer = relationship("User", back_populates="incomes")
#     # ✅ Relationships
#
#     farmer = relationship("User", back_populates="incomes")
#     farm = relationship("Farm", back_populates="incomes")
#     batch = relationship("Batch", back_populates="incomes")
#     unit = relationship("Unit", back_populates="incomes")
#
#     # farmer = relationship("User", backref="incomes")
#     # batch = relationship("Batch", backref="incomes")
#     # unit = relationship("Unit", backref="incomes")
#     # harvest = relationship("HarvestForm", backref="incomes", uselist=False)
#
#
# class Stocking(Base):
#     __tablename__ = "stockings"
#
#     id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
#     farmerId = Column(Integer, ForeignKey("users.id"), nullable=False)
#     batchId = Column(String(50), ForeignKey("batches.batchId"), nullable=False)
#     unitId = Column(String(50), ForeignKey("units.id"), nullable=False)
#     farmId = Column(Integer, ForeignKey("farms.id"), nullable=False)
#
#     fishType = Column(String(100), nullable=False)            # e.g., Tilapia
#     quantityPurchased = Column(Integer, nullable=False)       # total fingerlings stocked
#     totalAmount = Column(Float, nullable=False)               # purchase cost
#     date = Column(DateTime, default=datetime.utcnow)          # stocking date
#
#     createdAt = Column(DateTime, default=datetime.utcnow)
#     updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
#
#     # Relationships
#     farmer = relationship("User", back_populates="stockings")
#     farm = relationship("Farm", back_populates="stockings")
#     batch = relationship("Batch", back_populates="stockings")
#     unit = relationship("Unit", back_populates="stockings")



# class Product(Base):
#     __tablename__ = "products"
#     id = Column(Integer, primary_key=True, index=True, autoincrement=True)
#     title = Column(String(250), nullable=False)
#     description = Column(String(250), nullable=True)
#     image = Column(String(250), nullable=True)
#     price = Column(Float, nullable=False)
#     category = Column(String(250), nullable=False)
#     featured = Column(Boolean, default=False , nullable=True)
#     featureexpiredate = Column(Boolean , default=False, nullable=True)
#     quantity = Column(Integer, default=0)
#     # relationships
#
#     price_range = relationship("PriceRange", uselist=False,  back_populates="product")
#     types = relationship("ProductType", back_populates="product", cascade="all, delete-orphan")

# class Category(Base):
#     __tablename__ = "categories"
#     id = Column(Integer, primary_key=True, index=True, autoincrement=True)
#     name = Column(String(250), unique=True, nullable=False)
#
#     # Relationship back to products
#     products = relationship("Product", back_populates="category_obj")


# class Cart(Base):
#     __tablename__ = "cart"
#     id = Column(Integer, primary_key=True, index=True, autoincrement=True)
#     product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
#     type_id = Column(Integer, ForeignKey("product_types.id"), nullable=True)
#     quantity = Column(Integer, nullable=False)
#
#     product = relationship("Product")
#     selected_type = relationship("ProductType")
# class Cart(Base):
#     __tablename__ = "cart"
#     id = Column(Integer, primary_key=True, index=True, autoincrement=True)
#     product_id = Column(Integer, ForeignKey("products.id"))
#     quantity = Column(Integer, nullable=False)
#     product = relationship("Product")



# class Labs(Base):
#     __tablename__ = "labs"
#     id = Column(Integer, primary_key=True, index=True, autoincrement=True)
#     labtesttorun = Column(String(250), nullable=False)
#     selectspecfictest = Column(String(250), nullable=True)
#     date = Column(String(250), nullable=False)
#     username = Column(String(250), nullable=False)
#     # Order/payment tracking
#     status = Column(String(50), default="pending")  # pending, in_progress, completed
#     payment_status = Column(String(50), default="unpaid")  # unpaid, paid, failed
#     payment_reference = Column(String(250), nullable=True)  # from Paystack
#     amount = Column(Integer, nullable=False, default=0)  # cost of test
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


#
# class Labs(Base):
#     __tablename__ = "labs"
#     id = Column(Integer, primary_key=True, index=True, autoincrement=True)
#     username = Column(String(250), nullable=False)
#     date = Column(String(250), nullable=False)
#     discount = Column(Integer, default=0 ,  nullable=True)
#     totalprice = Column(Integer, nullable=False)
#     discounttotal = Column(Integer, nullable=True)
#     amount = Column(Integer, nullable=False)
#     payment_method = Column(String(50), nullable=False)
#     transaction_reference = Column(String(255), nullable=True)
#     payment_status = Column(String(50), default="pending")
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     # 🧩 Relationship to lab tests
#     tests = relationship("LabTest", back_populates="lab", cascade="all, delete-orphan")
#     # 🧩 Relationship back to User
#     user = relationship("User", back_populates="labs")



# class LabTest(Base):
#     __tablename__ = "lab_tests"
#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String(255), nullable=False)
#     test_name = Column(String(255), nullable=False)
#     price = Column(Float, nullable=False)
#     lab_id = Column(Integer, ForeignKey("labs.id"), nullable=False)
#     lab = relationship("Labs", back_populates="tests")



# class PriceRange(Base):
#     __tablename__ = "price_ranges"
#     id = Column(Integer, primary_key=True, index=True, autoincrement=True)
#     from_ = Column("from", Float, nullable=False)
#     to = Column(Float, nullable=False)
#     product_id = Column(Integer, ForeignKey("products.id"))
#     product = relationship("Product", back_populates="price_range")


# class ProductType(Base):
#     __tablename__ = "product_types"
#     id = Column(Integer, primary_key=True, index=True, autoincrement=True)
#     typeValue = Column(String(230), nullable=False)
#     valueMeasurement = Column(String(250), nullable=False)
#     valuePrice = Column(Float, nullable=False)
#     quantity = Column(Integer, default=0)
#     product_id = Column(Integer, ForeignKey("products.id"))
#     product = relationship("Product", back_populates="types")



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