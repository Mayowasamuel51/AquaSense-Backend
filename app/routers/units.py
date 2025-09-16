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

router = APIRouter(prefix="/units", tags=["units"])


# ✅ Get all units for the logged-in farmer
@router.get("/", response_model=list[UnitResponse])
def get_units(db: Session = Depends(get_db), user=Depends(get_current_user)):
    units = db.query(Unit).filter(Unit.farmerId == user.id).all()
    return units


# ✅ Get a single unit by ID
@router.get("/{unit_id}", response_model=UnitResponse)
def get_unit(unit_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    unit = db.query(Unit).filter(Unit.id == unit_id, Unit.farmerId == user.id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    return unit

@router.post("/", response_model=UnitResponse)
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
