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

router = APIRouter(prefix="/recording", tags=["recording"])


@router.post("/units", response_model=UnitResponse)
def create_unit(
    unit: UnitCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if user exists
    db_user = db.query(User).filter(User.id == user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    # Create the Unit
    db_unit = Unit(
        id=str(uuid.uuid4()),
        farmerId=user.id,
        pondName=unit.pondName,
        pondType=unit.pondType,
        pondCapacity=unit.pondCapacity,
        fishes=unit.fishes,
        imageUrl="http://example.com/image.jpg",  # you can make this dynamic later
        type=unit.type,
        isActive=unit.isActive
    )

    # Save to DB
    db.add(db_unit)
    db.commit()
    db.refresh(db_unit)

    return  db_unit



@router.get("/users/{user_id}/units", response_model=List[UnitResponse])
def get_user_units(user_id: int, db: Session = Depends(get_db)):
    units = db.query(Unit).filter(Unit.farmerId == user_id).all()
    return units


@router.get("/units/{unit_id}", response_model=UnitResponse)
def get_unit(unit_id: str, db: Session = Depends(get_db)):
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    return unit

# ======================
# Batch Endpoints
# ======================
@router.post("/batches",
             response_model=BatchResponse)
def create_batch(
        batch: BatchCreate,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db)):
    # Check if user exists
    db_user = db.query(User).filter(User.id == user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_batch = Batch(
        farmerId=user.id,
        batchId=str(uuid.uuid4()),
        batchName = batch.batchName,
        fish_type = batch.fish_type,
        number_of_fish = batch.number_of_fish,
        isCompleted = batch.isCompleted
    )
    db.add(db_batch)
    db.commit()
    db.refresh(db_batch)

    return db_batch


@router.get("/users/{user_id}/batches", response_model=List[BatchResponse])
def get_user_batches(user_id: int, db: Session = Depends(get_db)):
    batches = db.query(Batch).filter(Batch.farmerId == user_id).all()
    return batches


@router.get("/batches/{batch_id}", response_model=BatchResponse)
def get_batch(batch_id: str, db: Session = Depends(get_db)):
    batch = db.query(Batch).filter(Batch.batchId == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    return batch


# ======================
# Record Endpoints
# ======================
@router.post("/records", response_model=RecordResponse)
def create_record(record: RecordCreate, db: Session = Depends(get_db)):
    db_record = Record(**record.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


@router.get("/batches/{batch_id}/records", response_model=List[RecordResponse])
def get_records_by_batch(batch_id: str, db: Session = Depends(get_db)):
    records = db.query(Record).filter(Record.batchId == batch_id).all()
    return records


@router.get("/records/{record_id}", response_model=RecordResponse)
def get_record(record_id: str, db: Session = Depends(get_db)):
    record = db.query(Record).filter(Record.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


# ======================
# DailyRecord Endpoints
# ======================
@router.post("/daily-records", response_model=DailyRecordResponse)
def create_daily_record(daily: DailyRecordCreate, db: Session = Depends(get_db)):
    db_daily = DailyRecord(**daily.dict())
    db.add(db_daily)
    db.commit()
    db.refresh(db_daily)
    return db_daily


@router.get("/records/{record_id}/daily-records", response_model=List[DailyRecordResponse])
def get_daily_records(record_id: str, db: Session = Depends(get_db)):
    return db.query(DailyRecord).filter(DailyRecord.recordId == record_id).all()