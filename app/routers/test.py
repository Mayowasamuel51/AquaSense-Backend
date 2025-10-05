from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import TestCategory as TestCategoryModel

router = APIRouter(prefix="/tests", tags=["tests"])


# ------------------ Schemas ------------------
class TestOut(BaseModel):
    id: int
    name: str
    price: int

    class Config:
        from_attributes = True


class TestCategoryOut(BaseModel):
    id: int
    title: str
    tests: List[TestOut] = []

    class Config:
        from_attributes = True


# ------------------ Routes ------------------
@router.get("/", response_model=dict)
def get_tests(db: Session = Depends(get_db)):
    categories = db.query(TestCategoryModel).all()

    # ✅ Convert ORM objects to dicts using Pydantic models
    data = [TestCategoryOut.model_validate(cat).model_dump() for cat in categories]

    return {"data": data}


@router.get("/{category_id}", response_model=dict)
def get_test_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(TestCategoryModel).filter(TestCategoryModel.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Test category not found")

    data = TestCategoryOut.model_validate(category).model_dump()
    return {"data": data}
