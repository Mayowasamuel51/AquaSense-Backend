from __future__ import annotations

# from typing import Optional, List
# from datetime import datetime

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime





# syncschemas.py

# -------------------
# Finance / Expense Schemas
# -------------------

class IncomeIn(BaseModel):
    id: Optional[str] = None
    incomeType: Optional[str] = Field(None, alias="income_type")
    amountEarned: Optional[float] = Field(None, alias="amount_earned")
    amount: Optional[float] = None
    quantitySold: Optional[int] = Field(None, alias="quantity_sold")
    paymentMethod: Optional[str] = Field(None, alias="payment_method")
    date: Optional[datetime] = Field(None, alias="date")  # maps to income_date
    isSynced: Optional[int] = Field(None, alias="isSynced")
    createdAt: Optional[datetime] = Field(None, alias="createdAt")
    updatedAt: Optional[datetime] = Field(None, alias="updatedAt")

    class Config:
        allow_population_by_field_name = True
        orm_mode = True

class StockingIn(BaseModel):
    id: Optional[str] = None
    fishType: Optional[str] = Field(None, alias="fish_type")
    quantityPurchased: Optional[int] = Field(None, alias="quantity_purchased")
    totalAmount: Optional[float] = Field(None, alias="total_amount")
    date: Optional[datetime] = None
    isSynced: Optional[int] = Field(None, alias="isSynced")
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    class Config:
        allow_population_by_field_name = True
        orm_mode = True

class FeedIn(BaseModel):
    id: Optional[str] = None
    feedName: Optional[str] = Field(None, alias="feed_name")
    feedForm: Optional[str] = Field(None, alias="feed_form")
    feedSize: Optional[str] = Field(None, alias="feed_size")
    quantity: Optional[int] = None
    unit: Optional[str] = None
    costPerUnit: Optional[float] = Field(None, alias="cost_per_unit")
    totalAmount: Optional[float] = Field(None, alias="total_amount")
    date: Optional[datetime] = None
    isSynced: Optional[int] = Field(None, alias="isSynced")
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    class Config:
        allow_population_by_field_name = True
        orm_mode = True

class LabourIn(BaseModel):
    id: Optional[str] = None
    labourType: Optional[str] = Field(None, alias="labour_type")
    numberOfWorkers: Optional[int] = Field(None, alias="number_of_workers")
    totalAmount: Optional[float] = Field(None, alias="total_amount")
    date: Optional[datetime] = None
    paymentMethod: Optional[str] = Field(None, alias="payment_method")
    notes: Optional[str] = None
    isSynced: Optional[int] = Field(None, alias="isSynced")
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    class Config:
        allow_population_by_field_name = True
        orm_mode = True

class MedicationIn(BaseModel):
    id: Optional[str] = None
    medicationName: Optional[str] = Field(None, alias="medication_name")
    quantity: Optional[str] = None
    totalCost: Optional[float] = Field(None, alias="total_cost")
    datePaid: Optional[datetime] = Field(None, alias="date_paid")
    paymentMethod: Optional[str] = Field(None, alias="payment_method")
    notes: Optional[str] = None
    isSynced: Optional[int] = Field(None, alias="isSynced")
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    class Config:
        allow_population_by_field_name = True
        orm_mode = True

class MaintenanceIn(BaseModel):
    id: Optional[str] = None
    activityType: Optional[str] = Field(None, alias="activity_type")
    totalCost: Optional[float] = Field(None, alias="total_cost")
    datePaid: Optional[datetime] = Field(None, alias="date_paid")
    paymentMethod: Optional[str] = Field(None, alias="payment_method")
    notes: Optional[str] = None
    isSynced: Optional[int] = Field(None, alias="isSynced")
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    class Config:
        allow_population_by_field_name = True
        orm_mode = True

class LogisticsIn(BaseModel):
    id: Optional[str] = None
    activityType: Optional[str] = Field(None, alias="activity_type")
    totalCost: Optional[float] = Field(None, alias="total_cost")
    datePaid: Optional[datetime] = Field(None, alias="date_paid")
    paymentMethod: Optional[str] = Field(None, alias="payment_method")
    notes: Optional[str] = None
    isSynced: Optional[int] = Field(None, alias="isSynced")
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    class Config:
        allow_population_by_field_name = True
        orm_mode = True

class OperationalExpenseIn(BaseModel):
    id: Optional[str] = None
    expenseName: Optional[str] = Field(None, alias="expense_name")
    totalCost: Optional[float] = Field(None, alias="total_cost")
    datePaid: Optional[datetime] = Field(None, alias="date_paid")
    paymentMethod: Optional[str] = Field(None, alias="payment_method")
    notes: Optional[str] = None
    isSynced: Optional[int] = Field(None, alias="isSynced")
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    class Config:
        allow_population_by_field_name = True
        orm_mode = True

class FinanceIn(BaseModel):
    income: Optional[List[IncomeIn]] = []
    stocking: Optional[List[StockingIn]] = []
    feed: Optional[List[FeedIn]] = []
    labour: Optional[List[LabourIn]] = []
    medication: Optional[List[MedicationIn]] = []
    maintenance: Optional[List[MaintenanceIn]] = []
    logistics: Optional[List[LogisticsIn]] = []
    operationalExpenses: Optional[List[OperationalExpenseIn]] = Field([], alias="operationalExpenses")

    class Config:
        allow_population_by_field_name = True
        orm_mode = True
# -------------------------
# Daily Record
# -------------------------
class DailyRecordIn(BaseModel):
    id: Optional[str] = None
    recordId: Optional[str] = None
    farmerId: Optional[int] = None
    batchId: Optional[str] = None
    unitId: Optional[str] = None
    date: Optional[datetime] = None
    feedName: Optional[str] = None
    feedSize: Optional[str] = None
    feedQuantity: Optional[float] = None
    mortality: Optional[int] = None
    coins: Optional[int] = None
    isSynced: Optional[int] = 0
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


# -------------------------
# Weight Sampling
# -------------------------
class WeightSamplingIn(BaseModel):
    id: Optional[str] = None
    recordId: Optional[str] = None
    farmerId: Optional[int] = None
    batchId: Optional[str] = None
    unitId: Optional[str] = None
    sampleName: Optional[str] = None
    date: Optional[datetime] = None
    fishNumbers: Optional[int] = None
    totalWeight: Optional[float] = None
    completed: Optional[int] = None
    isSynced: Optional[int] = 0
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


# -------------------------
# Grade
# -------------------------
class GradeIn(BaseModel):
    id: Optional[str] = None
    sortingId: Optional[str] = None
    destinationBatchId: Optional[str] = None
    destinationBatchName: Optional[str] = None
    destinationUnitId: Optional[str] = None
    destinationUnitName: Optional[str] = None
    averageFishWeight: Optional[float] = None
    fishTransferred: Optional[int] = None
    sampleName: Optional[str] = None
    recordId: Optional[str] = None
    batchId: Optional[str] = None
    isSynced: Optional[int] = 0
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


# -------------------------
# Grading & Sorting
# -------------------------
class GradingAndSortingIn(BaseModel):
    id: Optional[str] = None
    recordId: Optional[str] = None
    farmerId: Optional[int] = None
    batchId: Optional[str] = None
    unitId: Optional[str] = None
    gradeWith: Optional[str] = None
    sampleName: Optional[str] = None
    date: Optional[datetime] = None
    gradingPondNumber: Optional[str] = None
    fishNumbers: Optional[int] = None
    totalWeight: Optional[float] = None
    completed: Optional[int] = None
    isSynced: Optional[int] = 0
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    grades: List[GradeIn] = Field(default_factory=list)


# -------------------------
# Harvest
# -------------------------
class HarvestIn(BaseModel):
    id: Optional[str] = None
    recordId: Optional[str] = None
    farmerId: Optional[int] = None
    batchId: Optional[str] = None
    unitId: Optional[str] = None
    date: Optional[datetime] = None
    salesInvoiceNumber: Optional[str] = None
    quantityHarvest: Optional[int] = None
    totalWeight: Optional[float] = None
    pricePerKg: Optional[float] = None
    totalSales: Optional[float] = None
    isSynced: Optional[int] = 0
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


# -------------------------
# Unit (full unit details from mobile)
# -------------------------
class UnitIn(BaseModel):
    id: Optional[str] = None
    farmerId: Optional[int] = None
    unitName: Optional[str] = None
    unitType: Optional[str] = None
    unitDimension: Optional[str] = None
    unitCapacity: Optional[int] = None
    fishes: Optional[int] = None
    imageFile: Optional[str] = None
    imageUrl: Optional[str] = None
    unitcategory: Optional[str] = None
    isActive: Optional[int] = 0
    isSynced: Optional[int] = 0
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


# -------------------------
# Unit Record
# -------------------------
class UnitRecordIn(BaseModel):
    id: Optional[str] = None
    farmerId: Optional[int] = None  # <- make optional
    # farmerId: Optional[int] = None
    batchId: Optional[str] = None
    unitId: Optional[str] = None
    stocknumber: Optional[int] = None
    movedfishes: Optional[int] = None
    mortality: Optional[int] = None
    fishleft: Optional[int] = None
    incomingfish: Optional[int] = None
    fishtype: Optional[str] = None
    stockedon: Optional[datetime] = None
    totalfishcost: Optional[float] = None
    isSynced: Optional[int] = 0
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    unit: Optional[UnitIn] = None
    dailyRecords: List[DailyRecordIn] = Field(default_factory=list)
    weightSamplings: List[WeightSamplingIn] = Field(default_factory=list)
    gradingAndSortings: List[GradingAndSortingIn] = Field(default_factory=list)
    harvests: List[HarvestIn] = Field(default_factory=list)


# -------------------------
# Batch
# -------------------------
class BatchIn(BaseModel):
    batchId: Optional[str] = None
    # farmerId: int
    farmerId: Optional[int] = None  # <- make optional
    batchName: Optional[str] = None
    fishtype: Optional[str] = None
    numberoffishes: Optional[int] = None
    averagebodyweight: Optional[float] = None
    ageAtStock: Optional[int] = None
    isCompleted: Optional[int] = 0
    isSynced: Optional[int] = 0
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    records: List[UnitRecordIn] = Field(default_factory=list)
