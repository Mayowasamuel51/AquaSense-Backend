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
class MainFeeds(BaseModel):
    message:str
    data:FeedResponse

@router.post("/", response_model=MainFeeds)
def create_feed(
    feed: FeedCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    db_user = db.query(User).filter(User.id == user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
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
        date=feed.date)
    db.add(db_feed)
    db.commit()
    db.refresh(db_feed)

    return {
        "message": "feed created",
        "data":db_feed
    }

class MainFeedResponseOut(BaseModel):
    message:str
    data:List[FeedResponse]

@router.get("/", response_model=MainFeedResponseOut)
def get_feeds(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    feedsall = db.query(Feed).filter(Feed.farmerId == user.id).all()
    return {
        "message":f"here are the feeds for this farmer -> { user.first_name }",
        "data":feedsall
    }