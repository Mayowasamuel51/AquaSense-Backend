import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy.orm import Session
from passlib.hash import argon2
from uuid import uuid4
from ..database  import get_db
from ..models import User, Product, PriceRange, Cart, ProductType
from ..schemas import (UserOut, FarmBase, UserCreate,
                       UnitCreate, UnitResponse,
                       BatchCreate, BatchResponse,
                       RecordCreate, RecordResponse,
                       DailyRecordCreate, DailyRecordResponse,
                       WeightSamplingCreate, WeightSamplingResponse,

                       ProductOut, CategoryOut, CategoryBase)
from typing import List


router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("/{category}", response_model=List[ProductOut])
def get_categories(category: str, db: Session = Depends(get_db)):
    products = db.query(Product).filter(Product.category == category).all()
    if not products:
        # Optional: return empty list instead of error
        return []
    return products


#
# @router.post("/", response_model=CategoryOut)
# def create_category(category: CategoryBase, db: Session = Depends(get_db)):
#     existing = db.query(Category).filter(Category.name == category.name).first()
#     if existing:
#         raise HTTPException(status_code=400, detail="Category already exists")
#
#     db_category = Category(name=category.name)
#     db.add(db_category)
#     db.commit()
#     db.refresh(db_category)
#     return db_category
# @router.get("/categories/{category_id}", response_model=List[ProductOut])
# def get_products_by_category(category_id: int, db: Session = Depends(get_db)):
#     category = db.query(Category).filter(Category.id == category_id).first()
#     if not category:
#         raise HTTPException(status_code=404, detail="Category not found")
#     return category.products
