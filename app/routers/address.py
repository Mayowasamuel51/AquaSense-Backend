from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import get_db
from ..models import DeliveryAddress, User
from ..dep.security import get_current_user

router = APIRouter(prefix="/address", tags=["Address"])

# 🧱 Pydantic model for input validation
class DeliveryAddressCreate(BaseModel):
    recipient_name: str
    phone_number: str
    address: str
    city: str
    state: str
    postal_code: str | None = None
    delivery_instructions: str | None = None


# 🚀 Route to add new delivery address
@router.post("/add", summary="Add a new delivery address")
def add_address(
    address_data: DeliveryAddressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ✅ verify user exists
    db_user = db.query(User).filter(User.id == current_user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # ✅ create a new delivery address
    new_address = DeliveryAddress(
        user_id=current_user.id,
        **address_data.dict()
    )

    # ✅ save it to database
    db.add(new_address)
    db.commit()
    db.refresh(new_address)

    return {
        "success": True,
        "message": "Address added successfully",
        "address": {
            "id": new_address.id,
            "recipient_name": new_address.recipient_name,
            "phone_number": new_address.phone_number,
            "address": new_address.address,
            "city": new_address.city,
            "state": new_address.state,
            "postal_code": new_address.postal_code,
            "delivery_instructions": new_address.delivery_instructions
        }
    }





# 🧱 Pydantic model for creating/updating delivery address
class DeliveryAddressCreate(BaseModel):
    recipient_name: str
    phone_number: str
    address: str
    city: str
    state: str
    postal_code: str | None = None
    delivery_instructions: str | None = None


# 🚀 Update route
@router.put("/update/{address_id}", summary="Update an existing delivery address")
def update_address(
    address_id: int,
    address_data: DeliveryAddressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ✅ Find the address owned by the current user
    delivery_address = (
        db.query(DeliveryAddress)
        .filter(
            DeliveryAddress.id == address_id,
            DeliveryAddress.user_id == current_user.id
        )
        .first()
    )

    if not delivery_address:
        raise HTTPException(status_code=404, detail="Address not found or unauthorized")

    # ✅ Update fields dynamically
    for key, value in address_data.dict().items():
        setattr(delivery_address, key, value)

    db.commit()
    db.refresh(delivery_address)

    return {
        "success": True,
        "message": "Address updated successfully",
        "address": {
            "id": delivery_address.id,
            "recipient_name": delivery_address.recipient_name,
            "phone_number": delivery_address.phone_number,
            "address": delivery_address.address,
            "city": delivery_address.city,
            "state": delivery_address.state,
            "postal_code": delivery_address.postal_code,
            "delivery_instructions": delivery_address.delivery_instructions
        }

    }





# 🚀 Get a single delivery address by ID
@router.get("/{address_id}", summary="Get a specific delivery address by ID")
def get_address_by_id(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    address = db.query(DeliveryAddress).filter(
        DeliveryAddress.id == address_id,
        DeliveryAddress.user_id == current_user.id
    ).first()

    if not address:
        raise HTTPException(status_code=404, detail="Address not found or unauthorized")

    return {
        "success": True,
        "message": "Address retrieved successfully",
        "address": {
            "id": address.id,
            "recipient_name": address.recipient_name,
            "phone_number": address.phone_number,
            "address": address.address,
            "city": address.city,
            "state": address.state,
            "postal_code": address.postal_code,
            "delivery_instructions": address.delivery_instructions
        }
    }