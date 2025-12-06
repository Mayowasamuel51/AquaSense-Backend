from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy.orm import Session
from passlib.hash import argon2
from uuid import uuid4
from ..database  import get_db
from ..models import User, Product, ProductType, Labs, SupportAgent
from ..schemas import (UserOut, FarmBase, UserCreate)
from typing import List
router = APIRouter(prefix="/supportagent", tags=["supportagent"])
from ..dep.security import create_tokens , get_current_user

class Agent(BaseModel):
    helpwith: str
    issue: str | None = None
    date: str
    # username: str  # required


@router.post("/")
def create_lab(agent:Agent,   user: User = Depends(get_current_user),db: Session = Depends(get_db)):
    # Check if user exists
    db_user = db.query(User).filter(User.id == user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    agent_form = SupportAgent(
        helpwith =agent.helpwith ,
        issue=agent.issue,
        date=agent.date,
        user_id= db_user.id,
        username=db_user.first_name,  # captured here
    )
    db.add(agent_form)
    db.commit()
    db.refresh(agent_form)

    return {"message": "", "agent_form": agent_form , "data":UserOut.from_orm(db_user) }


@router.get("/")
def get_all_labs(db: Session = Depends(get_db)):
    labs = db.query(SupportAgent).all()
    return {
        "message": "All Support form  retrieved successfully",
        "data": labs
    }
