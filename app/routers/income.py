import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy.orm import Session
from passlib.hash import argon2
from uuid import uuid4
from ..database  import get_db
from ..models import User, Farm, Unit, HarvestForm, WeightSampling, Record, Batch, DailyRecord, Feed, Income
from ..schemas import (UserOut, FarmBase, UserCreate,
                       UnitCreate, UnitResponse,
                       BatchCreate, BatchResponse,
                       RecordCreate, RecordResponse,
                       DailyRecordCreate, DailyRecordResponse,
                       WeightSamplingCreate, WeightSamplingResponse,
                       GradingAndSortingCreate, GradingAndSortingResponse,
                       GradeCreate, GradeResponse,
                       HarvestFormCreate, HarvestFormResponse, FeedResponse, FeedCreate, IncomeResponse, IncomeCreate)
from typing import List
# from ..dep.security import create_tokens
from ..dep.security import create_tokens , get_current_user

router = APIRouter(prefix="/income", tags=["income"])

class MainIncomeResponse (BaseModel):
    message:str
    data:IncomeResponse


@router.post("/", response_model=MainIncomeResponse)
def create_income(
    income: IncomeCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    db_user = db.query(User).filter(User.id == user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    # ✅ check batch exists
    batch_exists = db.query(Batch).filter(Batch.batchId == income.batchId).first()
    if not batch_exists:
        raise HTTPException(status_code=404, detail="Batch not found")

    # ✅ check unit exists
    unit_exists = db.query(Unit).filter(Unit.id == income.unitId).first()
    if not unit_exists:
        raise HTTPException(status_code=404, detail="Unit not found")
    farm = db.query(Farm).filter(Farm.owner_id == user.id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found for this user")
    # ✅ auto-fill pond name if not provided
    applied_pond_name = income.appliedToPondName or unit_exists.pondName
    db_income = Income(
        id=str(uuid.uuid4()),
        farmerId= user.id,
        farmId=farm.id,  # ✅ attach farmId
        batchId=batch_exists.batchId,
        unitId=unit_exists.id,
        appliedToPondName=applied_pond_name,
        incomeType=income.incomeType,
        amountEarned=income.amountEarned,
        quantitySold=income.quantitySold,
        paymentMethod=income.paymentMethod,
        incomeDate=income.incomeDate,
    )

    db.add(db_income)
    db.commit()
    db.refresh(db_income)

    return {
        "message":"your income has been created",
        "data":db_income
    }


@router.get("/", response_model=List[IncomeResponse])
def get_incomes(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    farmId: Optional[int] = Query(None),
    unitId: Optional[str] = Query(None),
    batchId: Optional[str] = Query(None),
    startDate: Optional[datetime] = Query(None),
    endDate: Optional[datetime] = Query(None),
):
    query = db.query(Income)

    if farmId:
        query = query.filter(Income.farmId == farmId)
    if unitId:
        query = query.filter(Income.unitId == unitId)
    if batchId:
        query = query.filter(Income.batchId == batchId)
    if startDate:
        query = query.filter(Income.incomeDate >= startDate)
    if endDate:
        query = query.filter(Income.incomeDate <= endDate)

    return query.all()