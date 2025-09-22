import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy.orm import Session
from passlib.hash import argon2
from uuid import uuid4
from ..database  import get_db
from ..models import User, Farm, Unit, HarvestForm, WeightSampling, Record, Batch, DailyRecord, Feed, Income, Stocking
from ..schemas import (UserOut, FarmBase, UserCreate,
                       UnitCreate, UnitResponse,
                       BatchCreate, BatchResponse,
                       RecordCreate, RecordResponse,
                       DailyRecordCreate, DailyRecordResponse,
                       WeightSamplingCreate, WeightSamplingResponse,
                       GradingAndSortingCreate, GradingAndSortingResponse,
                       GradeCreate, GradeResponse,
                       HarvestFormCreate, HarvestFormResponse, FeedResponse, FeedCreate, IncomeResponse, IncomeCreate,
                       StockingResponse, StockingCreate)
from typing import List
# from ..dep.security import create_tokens
from ..dep.security import create_tokens , get_current_user

router = APIRouter(prefix="/stocking", tags=["stocking"])


class MainStockingResponse (BaseModel):
    message:str
    data:StockingResponse


@router.post("/", response_model=MainStockingResponse)
def create_stocking(
    stocking: StockingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # ✅ Ensure batch and unit exist
    batch = db.query(Batch).filter(Batch.batchId == stocking.batchId).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    unit = db.query(Unit).filter(Unit.id == stocking.unitId).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")

    farm = db.query(Farm).filter(Farm.owner_id == user.id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    applied_pond_name = unit.pondName or  "helo"
    db_stocking = Stocking(
        id=str(uuid.uuid4()),
        farmerId=user.id,
        batchId=batch.batchId,
        unitId=unit.id,
        farmId=farm.id,
        # appliedToPondName=applied_pond_name,  # ✅ store pond name
        fishType=stocking.fishType,
        quantityPurchased=stocking.quantityPurchased,
        totalAmount=stocking.totalAmount,
        date=stocking.date,
    )

    db.add(db_stocking)
    db.commit()
    db.refresh(db_stocking)

    return {
        "message":"Stocking added to this pond ",
        "data":db_stocking
    }