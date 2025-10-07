from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import jwt
from ..database import get_db
from ..config import settings
from ..models import Vendor, Product, ProductType
from ..schemas import ProductCreate, ProductResponse

router = APIRouter(prefix="/vendor/products", tags=["Vendor Products"])

SECRET_KEY = settings.JWT_SECRET
ALGORITHM = "HS256"

# Helper: Decode vendor token
def get_current_vendor(token: str, db: Session) -> Vendor:
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


# 🧩 CREATE PRODUCT
@router.post("/", response_model=ProductResponse)
def create_product(
    body: ProductCreate,
    token: str,
    db: Session = Depends(get_db),
):
    vendor = get_current_vendor(token, db)

    # Extract price range safely
    price_from = body.price_range.from_ if body.price_range else None
    price_to = body.price_range.to if body.price_range else None

    # Create main product
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

    # Add product types (variations)
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

    return product
