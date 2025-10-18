from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload
import jwt
from ..database import get_db
from ..config import settings
from ..models import Vendor, Product, ProductType, User
from ..schemas import ProductCreate, ProductResponse
from ..dep.security import get_current_user
router = APIRouter(prefix="/products", tags=["Vendor Products"])

SECRET_KEY = settings.JWT_SECRET
ALGORITHM = "HS256"

# Define the Bearer auth dependency
security = HTTPBearer()


def get_current_vendor(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> Vendor:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    vendor = db.query(Vendor).filter(Vendor.email == email).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    return vendor
class MainVendorProductOut(BaseModel):
    message:str
    data:ProductResponse

@router.post("/", response_model=MainVendorProductOut)
def create_product(
    body: ProductCreate,
    vendor: Vendor = Depends(get_current_vendor),
    db: Session = Depends(get_db),
):
    # Extract price range safely
    price_from = body.price_range.from_ if body.price_range else None
    price_to = body.price_range.to if body.price_range else None

    # Create product
    product = Product(
        title=body.title,
        description=body.description,
        image=body.image,
        price=body.price,
        category=body.category,
        price_from=price_from,
        price_to=price_to,
        discount_percent=body.discount_percent,
        discount_amount=body.discount_amount,
        vendor_id=vendor.id,
    )

    # Add product types
    for t in body.types:
        ptype = ProductType(
            type_value=t.typeValue,
            value_measurement=t.valueMeasurement,
            value_price=t.valuePrice,
        )
        product.types.append(ptype)

    db.add(product)
    db.commit()
    db.refresh(product)

    return {"message":"You have created a product ","data": product}

class VendorPublic(BaseModel):
    id: int
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    city: Optional[str]
    address: Optional[str]
    state: Optional[str]
    area: Optional[str]
    pick_up_station_address : Optional[str]
    opening_hour: Optional[str]
    profilepicture: Optional[str]
    kyc_status: Optional[str]

    class Config:
        from_attributes = True


# --- Product Type ---
class ProductTypeResponse(BaseModel):
    id: int
    type_value: str
    value_measurement: str
    value_price: float

    class Config:
        from_attributes = True


# --- Product ---
class ProductResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    image: Optional[str]
    price: float
    category: Optional[str]
    price_from: Optional[float]
    price_to: Optional[float]
    discount_percent: Optional[float]
    discount_amount: Optional[float]
    featured: Optional[bool] = False
    featured_expiry_date: Optional[datetime]
    vendor: VendorPublic                 # ✅ include vendor info
    types: List[ProductTypeResponse] = []

    class Config:
        from_attributes = True


# --- Main Response Wrapper ---
class MainProductOutResponse(BaseModel):
    message: str
    data: List[ProductResponse]



@router.get("/", response_model=MainProductOutResponse)
def get_all_products(user: User = Depends(get_current_user),db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    products = db.query(Product).options(
        joinedload(Product.types),
        joinedload(Product.vendor)  # ✅ load vendor relationship
    ).all()

    return {
        "message": "showing all product",
        "data": products
    }

























#
#
# class MainProductOutResponse (BaseModel):
#     message:str
#     data:List[ProductResponse]
#
# @router.get("/", response_model=MainProductOutResponse)
# def get_all_products(db: Session = Depends(get_db)):
#     products = db.query(Product).options(joinedload(Product.types)).all()
#     return {
#         "message":"showing all product",
#         "data":products
#     }


# @router.get("/", response_model=MainProductOutResponse)
# def get_products(
#     db: Session = Depends(get_db),
#     sort: Optional[str] = Query(None, description="Sort: newest, featured, price_low, price_high")
# ):
#     query = db.query(Product)
#
#     # Apply sorting
#     if sort == "newest":
#         query = query.order_by(Product.id.desc())  # assuming higher ID = newer
#     elif sort == "featured":
#         query = query.filter(Product.featured == True).order_by(Product.id.desc())
#     elif sort == "price_low":
#         query = query.order_by(Product.price.asc())
#     elif sort == "price_high":
#         query = query.order_by(Product.price.desc())
#     products = query.all()
#     if not products:
#         raise HTTPException(status_code=404, detail="No products found in the database")
#     return {"message": "showing all products", "data": products}
#
# @router.get("/{product_id}", response_model=MainProductOut)
# def get_product(product_id: int, db: Session = Depends(get_db)):
#     product = db.query(Product).filter(Product.id == product_id).first()
#     if not product:
#         raise HTTPException(
#             status_code=404,
#             detail=f"Product with id {product_id} not found"
#         )
#     return {"message": "Product retrieved successfully", "data": product}


