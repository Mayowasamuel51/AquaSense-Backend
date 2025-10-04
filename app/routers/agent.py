from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy.orm import Session
from passlib.hash import argon2
from uuid import uuid4
from ..database  import get_db
from ..models import User, Product, PriceRange, Cart, ProductType, Labs, SupportAgent
from ..schemas import (UserOut, FarmBase, UserCreate, ProductOut)
from typing import List
router = APIRouter(prefix="/supportagent", tags=["supportagent"])


class Agent(BaseModel):
    helpwith: str
    issue: str | None = None
    date: str
    username: str  # required


@router.post("/")
def create_lab(agent:Agent, db: Session = Depends(get_db)):
    agent_form = SupportAgent(
        helpwith =agent.helpwith ,
        issue=agent.issue,
        date=agent.date,
        username=agent.username  # captured here
    )
    db.add(agent_form)
    db.commit()
    db.refresh(agent_form)

    return {"message": "", "Hello an Agent will attend to you ": agent_form}


@router.get("/")
def get_all_labs(db: Session = Depends(get_db)):
    labs = db.query(SupportAgent).all()
    return {
        "message": "All Support form  retrieved successfully",
        "data": labs
    }
