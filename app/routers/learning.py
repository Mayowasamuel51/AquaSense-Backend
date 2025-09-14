from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from passlib.hash import argon2
from uuid import uuid4
# from ..schemas import UserLearning
from typing import List
from ..database  import get_db
from ..models import User, Video, Test, Module, UserVideoProgress, UserTestProgress, Option, UserTestAnswer
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
def answer_test(body: AnswerTestIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    test = db.query(Test).filter(Test.id == body.test_id).first()
    if not test:
        raise HTTPException(404, "Test not found")

    option = db.query(Option).filter(Option.id == body.option_id, Option.test_id == body.test_id).first()
    if not option:
        raise HTTPException(400, "Invalid option for this test")

    is_correct = option.id == test.correct_option_id

    progress = db.query(UserTestProgress).filter_by(user_id=user.id, test_id=body.test_id).first()
    if not progress:
        progress = UserTestProgress(
            user_id=user.id,
            test_id=body.test_id,
            selected_option_id=body.option_id,
            is_correct=is_correct
        )
        db.add(progress)
    else:
        progress.selected_option_id = body.option_id
        progress.is_correct = is_correct

    if is_correct:
        user.coins += 50

    db.commit()

    return {
        "message": "Answer submitted",
        "testId": body.test_id,
        "selectedOptionId": body.option_id,
        "isCorrect": is_correct,
        "total_coins": user.coins
    }


# class AnswerIn(BaseModel):
#     testId: str
#     selectedOptionId: str
class AnswerIn(BaseModel):
    testId: str
    selectedOptionId: str

@router.post("/answer")
def submit_answer(
    body: AnswerIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # check that test exists
    test = db.query(Test).filter(Test.id == body.testId).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    # check option belongs to this test
    option = db.query(Option).filter(
    Option.id == body.selectedOptionId,
        Option.test_id == body.testId
    ).first()
    if not option:
        raise HTTPException(status_code=400, detail="Invalid option for this test")

    # check if user already answered
    existing_answer = db.query(UserTestAnswer).filter(
        UserTestAnswer.user_id == user.id,
        UserTestAnswer.test_id == body.testId
    ).first()

    if existing_answer:
        # update existing answer
        existing_answer.selected_option_id = body.selectedOptionId
    else:
        # create new answer
        new_answer = UserTestAnswer(
            user_id=user.id,
            test_id=body.testId,
            selected_option_id=body.selectedOptionId
        )
        db.add(new_answer)

    db.commit()

    is_correct = body.selectedOptionId == test.correct_option_id

    return {
        "message": "Answer submitted",
        "testId": test.id,
        "selectedOptionId": body.selectedOptionId,
        "isCorrect": is_correct
    }













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
