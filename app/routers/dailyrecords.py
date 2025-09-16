import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy.orm import Session
from passlib.hash import argon2
from uuid import uuid4
from ..database  import get_db
from ..models import User, Farm, Unit, HarvestForm, WeightSampling, Record, Batch, DailyRecord
from ..schemas import ( UserOut ,  FarmBase ,  UserCreate,
    UnitCreate, UnitResponse,
    BatchCreate, BatchResponse,
    RecordCreate, RecordResponse,
    DailyRecordCreate, DailyRecordResponse,
    WeightSamplingCreate, WeightSamplingResponse,
    GradingAndSortingCreate, GradingAndSortingResponse,
    GradeCreate, GradeResponse,
    HarvestFormCreate, HarvestFormResponse)
from typing import List
# from ..dep.security import create_tokens
from ..dep.security import create_tokens , get_current_user

router = APIRouter(prefix="/daily-records", tags=["daily-records"])


@router.post("/", response_model=DailyRecordResponse)
def create_daily_record(
    daily_record: DailyRecordCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if user exists
    db_user = db.query(User).filter(User.id == user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
        # 1. Find the active record (farmer + batch + unit)
    record = (
        db.query(Record)
        .filter(Record.farmerId == user.id)
        .order_by(Record.createdAt.desc())  # 👈 or however you decide "active"
        .first()
    )

    if not record:
        raise HTTPException(status_code=404, detail="No active record found for this farmer")

    # 2. Create DailyRecord
    db_daily = DailyRecord(
        id=str(uuid.uuid4()),
        recordId=record.id,
        farmerId=user.id,
        batchId=record.batchId,
        unitId=record.unitId,
        feedName=daily_record.feedName,
        feedSize=daily_record.feedSize,
        feedQuantity=daily_record.feedQuantity,
        mortality=daily_record.mortality,
        date=daily_record.date,
        coins=10,
    )
    db.add(db_daily)
    db.commit()
    db.refresh(db_daily)

    return db_daily
