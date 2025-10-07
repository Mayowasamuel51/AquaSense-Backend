from fastapi import APIRouter, Depends, HTTPException, Query, Body
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy.orm import Session
from passlib.hash import argon2
from uuid import uuid4
from ..database  import get_db
from ..models import User, Labs, SupportTicket
from ..schemas import (UserOut, FarmBase, UserCreate)
from typing import List
from ..dep.security import create_tokens , get_current_user

router = APIRouter(prefix="/farmsupport", tags=["farmsupport"])


class SupportTicketCreate(BaseModel):
    category: str   # restricted to the 3 options
    message: Optional[str] = None
    farmer_name: Optional[str] = None


class SupportTicketOut(BaseModel):
    id: int
    category: str
    message: Optional[str]
    response: Optional[str] = None
    status: str
    farmer_name: Optional[str]
    user_id:int
    class Config:
        from_attributes = True
    # model_config = dict(from_attributes=True)

# @router.post("/", response_model=SupportTicketOut)
# def create_ticket(ticket: SupportTicketCreate, user: User = Depends(get_current_user),db: Session = Depends(get_db)):
#     # db_user = db.query(User).filter(User.id == user.id).first()
#     # if not db_user:
#     #     raise HTTPException(status_code=404, detail="User not found")
#     allowed_categories = ["Emergency on the farm", "Existing order", "Bulk purchase"]
#     if ticket.category not in allowed_categories:
#         raise HTTPException(status_code=400, detail="Invalid category")
#
#     new_ticket = SupportTicket(
#         category=ticket.category,
#         message=ticket.message,
#         farmer_name=ticket.farmer_name
#     )
#     db.add(new_ticket)
#     db.commit()
#     db.refresh(new_ticket)
#     return new_ticket

@router.post("/", response_model=SupportTicketOut)
def create_ticket(
    ticket: SupportTicketCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.id == user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Decide the answer and default message
    if ticket.category == "Bulk purchase":
        auto_response = (
            "Thank you for your interest in bulk purchases! "
            "Our sales team will contact you shortly, or you can reach us at sales@farm.com."
        )
        default_message = "I want to make a bulk purchase."
    elif ticket.category == "Existing order":
        auto_response = (
            "Your order is currently being processed. "
            "You can track its status in your account under 'My Orders' or call support at 0800-123-999."
        )
        default_message = "I have a question about my existing order."
    elif ticket.category == "Emergency on the farm":
        auto_response = (
            "This seems urgent! Please call our emergency hotline immediately: 0800-123-456. "
            "Our support team will guide you."
        )
        default_message = "I have an emergency on my farm."
    else:
        raise HTTPException(status_code=400, detail="Invalid category")

    # If user didn't type a message, fill it with default
    ticket_message = ticket.message or default_message

    new_ticket = SupportTicket(
        category=ticket.category,
        message=ticket_message,
        farmer_name=db_user.first_name,
        user_id=db_user.id,
        response=auto_response,
        status="answered"
    )

    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    return new_ticket





@router.get("/", response_model=List[SupportTicketOut])
def list_tickets(db: Session = Depends(get_db)):
    return db.query(SupportTicket).all()

class MainoutTicket(BaseModel):
    data:List[SupportTicketOut]
    message:str
@router.get("/my-tickets", response_model=MainoutTicket)
def list_my_tickets(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Returns only the support tickets submitted by the currently logged-in farmer.
    """
    db_user = db.query(User).filter(User.id == user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    tickets = db.query(SupportTicket).filter(SupportTicket.user_id == user.id).all()
    return {"message":f"Hello {db_user.first_name} here your support messages",   "data":tickets}


@router.put("/{ticket_id}/respond", response_model=SupportTicketOut)
def respond_to_ticket(ticket_id: int, response: str = Body(...), db: Session = Depends(get_db)):
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    ticket.response = response
    ticket.status = "answered"
    db.commit()
    db.refresh(ticket)
    return ticket
