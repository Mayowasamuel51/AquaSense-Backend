import os
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import TestCategory as TestCategoryModel
from ..models import TestItem as TestItemModel

router = APIRouter(prefix="/tests", tags=["tests"])


# ------------------ Schemas ------------------
class TestBase(BaseModel):
    name: str
    price: int


class TestOut(TestBase):
    id: int

    class Config:
        from_attributes = True


class TestCategoryBase(BaseModel):
    title: str


class TestCategoryOut(TestCategoryBase):
    id: int
    tests: List[TestOut] = []

    class Config:
        from_attributes = True


# ------------------ Routes ------------------
@router.get("/", response_model=List[TestCategoryOut])
def get_tests(db: Session = Depends(get_db)):
    """
    Fetch all test categories with their test items from DB.
    """
    categories = db.query(TestCategoryModel).all()
    return categories


@router.get("/{category_id}", response_model=TestCategoryOut)
def get_test_category(category_id: int, db: Session = Depends(get_db)):
    """
    Fetch a single test category by ID.
    """
    category = db.query(TestCategoryModel).filter(TestCategoryModel.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Test category not found")
    return category
