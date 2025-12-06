import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy.orm import Session
from passlib.hash import argon2
from uuid import uuid4
from ..database  import get_db
from ..models import User, Farm, Unit, Harvest, WeightSampling, UnitRecord, Batch, DailyRecord
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

router = APIRouter(prefix="/batch", tags=["batch"])



class MainBatchResponse(BaseModel):
    message: str
    batch: BatchResponse
    user: UserOut

class AllMainBatchResponse(BaseModel):
    message: str
    batches: List[BatchResponse]
    user: UserOut
@router.post("/",
             response_model=MainBatchResponse)
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
        fishtype = batch.fishtype,
        numberoffishes = batch.numberoffishes,
        isCompleted = batch.isCompleted
    )
    db.add(db_batch)
    db.commit()
    db.refresh(db_batch)

    # return db_batch

    return  {
        "message":"You have created your Unit successfully",
        "batch":db_batch ,
        "user":db_user
    }


@router.get("/users/{user_id}/batches", response_model=AllMainBatchResponse)
def get_user_batches(user_id: int,   user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User batches  not found")
    batches = db.query(Batch).filter(Batch.farmerId == user_id).all()
    # return batches
    return {
        "message": "These are all your Batches ",
        "batches": batches,
        "user": db_user
    }


@router.get("/batches/{batch_id}", response_model=MainBatchResponse)
def get_batch(batch_id: str,   user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    batch = db.query(Batch).filter(Batch.batchId == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    # return batch
    return {
        "message": "This is one batch for yours ",
        "batch": batch,
        "user": db_user
    }

