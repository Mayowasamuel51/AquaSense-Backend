import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy.orm import Session
from passlib.hash import argon2
from uuid import uuid4
from ..database  import get_db
from ..models import User, Product, PriceRange, Cart, ProductType
from ..schemas import (UserOut, FarmBase, UserCreate, ProductCreate,ProductOut)
from typing import List
from ..dep.security import create_tokens , get_current_user

router = APIRouter(prefix="/products", tags=["products"])

class MainProductOut(BaseModel) :
    message:str
    data:ProductOut


@router.post("/", response_model=MainProductOut)
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

    return {"message":"product created " ,"data":db_product}

class MainProductOutResponse (BaseModel):
    message:str
    data:List[ProductOut]

@router.get("/", response_model=MainProductOutResponse)
def get_products(
    db: Session = Depends(get_db),
    sort: Optional[str] = Query(None, description="Sort: newest, featured, price_low, price_high")
):
    query = db.query(Product)

    # Apply sorting
    if sort == "newest":
        query = query.order_by(Product.id.desc())  # assuming higher ID = newer
    elif sort == "featured":
        query = query.filter(Product.featured == True).order_by(Product.id.desc())
    elif sort == "price_low":
        query = query.order_by(Product.price.asc())
    elif sort == "price_high":
        query = query.order_by(Product.price.desc())
    products = query.all()
    if not products:
        raise HTTPException(status_code=404, detail="No products found in the database")
    return {"message": "showing all products", "data": products}

@router.get("/{product_id}", response_model=MainProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=404,
            detail=f"Product with id {product_id} not found"
        )
    return {"message": "Product retrieved successfully", "data": product}



# # ✅ Fetch all products
# @router.get("/", response_model=List[ProductOut])
# def get_products(db: Session = Depends(get_db)):
#     return db.query(Product).all()
# @router.get("/", response_model=MainProductOutResponse)
# def get_products(db: Session = Depends(get_db)):
#     products = db.query(Product).all()
#     if not products:
#         raise HTTPException(
#             status_code=404,
#             detail="No products found in the database"
#         )
#     return {"message":"showing all products","data":products}