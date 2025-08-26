from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from passlib.hash import argon2
from uuid import uuid4
from ..schemas import UserLearning
from typing import List
from ..database  import get_db
from ..models import User , Learn
from ..dep.security import create_tokens , get_current_user

router = APIRouter(
    prefix="/learning",
     tags=["learning"],)

class Learning(BaseModel):
    email: EmailStr | None = None
    video_lenght :str
    first_question: str
    second_question :str
    third_question :str
    fourth_question : str


@router.post("/learning")
def learning(body: Learning,   user: User = Depends(get_current_user),   db: Session = Depends(get_db)):
    learning_entry = Learn(
        user_id=user.id,
        video_lenght =body.video_lenght ,
        first_question=body.first_question,
        second_question=body.second_question,
        third_question=body.third_question,
        fourth_question=body.fourth_question,
    )
    db.add(learning_entry)
    db.commit()
    db.refresh(learning_entry)
    return {
        "message": "Learning data saved successfully",
        "id": learning_entry.id,
        # "user": user.id,   #
    }
@router.get('/learning', response_model=List[UserLearning])
def getlearning(db: Session = Depends(get_db)):
    users = db.query(Learn).all()
    return users



