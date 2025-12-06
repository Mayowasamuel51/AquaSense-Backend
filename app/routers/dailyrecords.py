import uuid
from datetime import datetime

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


# ✅ Get all daily records for farmer
@router.get("/", response_model=list[DailyRecordResponse])
def get_daily_records(db: Session = Depends(get_db), user=Depends(get_current_user)):
    records = db.query(DailyRecord).filter(DailyRecord.farmerId == user.id).all()
    return records


# ✅ Get single daily record
@router.get("/{record_id}", response_model=DailyRecordResponse)
def get_daily_record(record_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    record = (
        db.query(DailyRecord)
        .filter(DailyRecord.id == record_id, DailyRecord.farmerId == user.id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Daily record not found")
    return record


@router.post("/", response_model=DailyRecordResponse)
def create_daily_record(
    daily: DailyRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Get the farmer’s active record
    record = (
        db.query(Record)
        .filter(Record.farmerId == current_user.id)
        .order_by(Record.createdAt.desc())
        .first()
    )

    if not record:
        raise HTTPException(status_code=404, detail="No active record found for this farmer")

    # 2. Auto-fill batchId and unitId from the record
    db_daily_record = DailyRecord(
        id=str(uuid.uuid4()),
        recordId=record.id,
        farmerId=current_user.id,
        batchId=record.batchId,
        unitId=record.unitId,
        date=daily.date,
        feedName=daily.feedName,
        feedSize=daily.feedSize,
        feedQuantity=daily.feedQuantity,
        mortality=daily.mortality,
    )

    db.add(db_daily_record)
    db.commit()
    db.refresh(db_daily_record)
    return db_daily_record
