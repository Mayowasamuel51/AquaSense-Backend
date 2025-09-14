from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from passlib.hash import argon2
from uuid import uuid4
# from ..schemas import UserLearning
from typing import List
from ..database  import get_db
from ..models import User, Video, Test, Module, UserVideoProgress, UserTestProgress ,Option
from ..dep.security import create_tokens , get_current_user
from ..schemas import ModuleOut, AnswerTestIn

#
router = APIRouter(
    prefix="/learning",
     tags=["learning"],)



# ✅ Get all modules with videos + tests
@router.get("/", response_model=list[ModuleOut])
def get_modules(db: Session = Depends(get_db)):
    return db.query(Module).all()


# ✅ Mark video as watched
@router.post("/videos/{video_id}/watch")
def watch_video(video_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(404, "Video not found")

    progress = db.query(UserVideoProgress).filter_by(user_id=user.id, video_id=video_id).first()
    if not progress:
        progress = UserVideoProgress(user_id=user.id, video_id=video_id, is_watched=True)
        db.add(progress)
        user.coins += video.coins
    else:
        if not progress.is_watched:
            progress.is_watched = True
            user.coins += video.coins

    db.commit()
    return {"message": "Video marked as watched", "earned": video.coins, "total_coins": user.coins}


# ✅ Answer a test question
@router.post("/tests/answer")
def answer_test(body: AnswerTestIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    test = db.query(Test).filter(Test.id == body.test_id).first()
    if not test:
        raise HTTPException(404, "Test not found")

    option = db.query(Option).filter(Option.id == body.option_id).first()
    if not option:
        raise HTTPException(404, "Option not found")

    is_correct = (test.correct_option_id == option.id)

    progress = db.query(UserTestProgress).filter_by(user_id=user.id, test_id=body.test_id).first()
    if not progress:
        progress =UserTestProgress(user_id=user.id, test_id=body.test_id,
                                           user_option_id=body.option_id, is_correct=is_correct)
        db.add(progress)
        if is_correct:
            user.coins += 50  # example coins for correct answer
    else:
        progress.user_option_id = body.option_id
        progress.is_correct = is_correct
        if is_correct:
            user.coins += 50  # prevent double reward by checking history

    db.commit()
    return {"message": "Answer submitted", "is_correct": is_correct, "total_coins": user.coins}
















# class Learning(BaseModel):
#     email: EmailStr | None = None
#     video_lenght :str
#     first_question: str
#     second_question :str
#     third_question :str
#     fourth_question : str
#
#
# @router.post("/")
# def learning(body: Learning,   user: User = Depends(get_current_user),   db: Session = Depends(get_db)):
#     learning_entry = Learn(
#         user_id=user.id,
#         video_lenght =body.video_lenght ,
#         first_question=body.first_question,
#         second_question=body.second_question,
#         third_question=body.third_question,
#         fourth_question=body.fourth_question,
#     )
#     db.add(learning_entry)
#     db.commit()
#     db.refresh(learning_entry)
#     return {
#         "message": "Learning data saved successfully",
#         "id": learning_entry.id,
#         # "user": user.id,   #
#     }
# @router.get('/', response_model=List[UserLearning])
# def getlearning(db: Session = Depends(get_db)):
#     users = db.query(Learn).all()
#     return users
#
#
#
