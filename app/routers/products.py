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
                       GradingAndSortingCreate, GradingAndSortingResponse,
                       GradeCreate, GradeResponse,
                       HarvestFormCreate, HarvestFormResponse, CartOut, CartItem, ProductCreate,
                       ProductOut)
from typing import List
# from ..dep.security import create_tokens
from ..dep.security import create_tokens , get_current_user

router = APIRouter(prefix="/products", tags=["products"])
@router.post("/", response_model=ProductOut)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    existing = db.query(Product).filter(Product.title == product.title).first()
    if existing:
        raise HTTPException(status_code=400, detail="Product already exists")
    db_product = Product(
        title=product.title,
        description=product.description,
        image=product.image,
        price=product.price,
        category=product.category,
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    # ✅ create price range only if provided
    if product.priceRange:
        price_range = PriceRange(
            from_=product.priceRange.from_,
            to=product.priceRange.to,
            product=db_product,  # ✅ safer way to attach
        )
        db.add(price_range)
        db.commit()
        db.refresh(db_product)

    # ✅ create product types
    for t in product.types or []:
        db_type = ProductType(
            typeValue=t.typeValue,
            valueMeasurement=t.valueMeasurement,
            valuePrice=t.valuePrice,
            quantity=t.quantity,
            product_id=db_product.id,
        )
        db.add(db_type)

    db.commit()
    db.refresh(db_product)

    return db_product


# ✅ Fetch all products
@router.get("/", response_model=List[ProductOut])
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).all()