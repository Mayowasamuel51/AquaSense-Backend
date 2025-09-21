import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy.orm import Session
from passlib.hash import argon2
from uuid import uuid4
from ..database  import get_db
from ..models import User, Farm, Unit, HarvestForm, WeightSampling, Record, Batch, DailyRecord, Feed
from ..schemas import (UserOut, FarmBase, UserCreate,
                       UnitCreate, UnitResponse,
                       BatchCreate, BatchResponse,
                       RecordCreate, RecordResponse,
                       DailyRecordCreate, DailyRecordResponse,
                       WeightSamplingCreate, WeightSamplingResponse,
                       GradingAndSortingCreate, GradingAndSortingResponse,
                       GradeCreate, GradeResponse,
                       HarvestFormCreate, HarvestFormResponse, FeedResponse, FeedCreate)
from typing import List
# from ..dep.security import create_tokens
from ..dep.security import create_tokens , get_current_user

router = APIRouter(prefix="/feeds", tags=["feeds"])


@router.post("/", response_model=FeedResponse)
def create_feed(
    feed: FeedCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # ✅ ensure foreign keys exist
    batch_exists = db.query(Batch).filter(Batch.batchId == feed.batchId).first()
    unit_exists = db.query(Unit).filter(Unit.id == feed.unitId).first()

    if not batch_exists:
        raise HTTPException(status_code=404, detail="Batch not found")
    if not unit_exists:
        raise HTTPException(status_code=404, detail="Unit not found")

    db_feed = Feed(
        id=str(uuid.uuid4()),
        farmerId=user.id,
        batchId=batch_exists.batchId,  # make sure we pass the string id
        unitId=unit_exists.id,
        feedName=feed.feedName,
        feedForm=feed.feedForm,
        feedSize=feed.feedSize,
        quantity=feed.quantity,
        # unit=feed.unit
    unitMeasure=feed.unitMeasure,
        costPerUnit=feed.costPerUnit,
        totalAmount=feed.totalAmount,
        date=feed.date,
    )

    db.add(db_feed)
    db.commit()
    db.refresh(db_feed)

    return db_feed


@router.get("/", response_model=list[FeedResponse])
def get_feeds(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Feed).filter(Feed.farmerId == user.id).all()