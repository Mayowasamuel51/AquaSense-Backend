from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy.orm import Session
from passlib.hash import argon2
from uuid import uuid4
from ..database  import get_db
from ..models import User ,     Farm , Unit , HarvestForm ,WeightSampling ,Record, Batch
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
router = APIRouter(prefix="/recording", tags=["rocording"])


@router.post("/units", response_model=UnitResponse)
def create_unit(unit: UnitCreate, db: Session = Depends(get_db)):
    db_unit = Unit(**unit.dict())
    db.add(db_unit)
    db.commit()
    db.refresh(db_unit)
    return db_unit