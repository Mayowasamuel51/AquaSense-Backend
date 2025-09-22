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


class ModulesResponse(BaseModel):
    data:list[ModuleOut]

class MainOutResponse (BaseModel):
    data:ModuleOut

# ✅ Get all modules with videos + tests
@router.get("/", response_model=ModulesResponse)
def get_modules(db: Session = Depends(get_db)):
    modules = db.query(Module).all()
    return {"data": modules}  # 👈 returns a DICT, not a list

@router.get("/{module_id}", response_model=MainOutResponse)
def get_module(module_id: int, db: Session = Depends(get_db)):
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    return {"data": module}


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

#
# # ✅ Answer a test question
# @router.post("/tests/answer")
# def answer_test(body: AnswerTestIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
#     test = db.query(Test).filter(Test.id == body.test_id).first()
#     if not test:
#         raise HTTPException(404, "Test not found")
#
#     option = db.query(Option).filter(Option.id == body.option_id, Option.test_id == body.test_id).first()
#     if not option:
#         raise HTTPException(400, "Invalid option for this test")
#
#     is_correct = option.id == test.correct_option_id
#
#     progress = db.query(UserTestProgress).filter_by(user_id=user.id, test_id=body.test_id).first()
#     if not progress:
#         progress = UserTestProgress(
#             user_id=user.id,
#             test_id=body.test_id,
#             selected_option_id=body.option_id,
#             is_correct=is_correct
#         )
#         db.add(progress)
#     else:
#         progress.selected_option_id = body.option_id
#         progress.is_correct = is_correct
#
#     if is_correct:
#         user.coins += 50
#
#     db.commit()
#
#     return {
#         "message": "Answer submitted",
#         "testId": body.test_id,
#         "selectedOptionId": body.option_id,
#         "isCorrect": is_correct,
#         "total_coins": user.coins
#     }


# class AnswerIn(BaseModel):
#     testId: str
# #     selectedOptionId: str
# class AnswerIn(BaseModel):
#     testId: str
#     selectedOptionId: str


@router.get("/progress")
def get_user_progress(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    # --- User total coins ---
    total_coins = user.coins

    # --- Count modules ---
    total_modules = db.query(Module).count()

    # --- Videos watched ---
    videos_watched = db.query(UserVideoProgress).filter_by(user_id=user.id, is_watched=True).count()

    # --- Tests answered ---
    tests_answered = db.query(UserTestProgress).filter_by(user_id=user.id).count()
    tests_correct = db.query(UserTestProgress).filter_by(user_id=user.id, is_correct=True).count()

    # --- Completed modules (all tests + video watched) ---
    completed_modules = 0
    modules = db.query(Module).all()
    for module in modules:
        videos = [v.id for v in module.videos]
        tests = [t.id for t in module.tests]

        watched_all = db.query(UserVideoProgress).filter(
            UserVideoProgress.user_id == user.id,
            UserVideoProgress.video_id.in_(videos),
            UserVideoProgress.is_watched == True
        ).count() == len(videos)

        answered_all = db.query(UserTestProgress).filter(
            UserTestProgress.user_id == user.id,
            UserTestProgress.test_id.in_(tests)
        ).count() == len(tests)

        if watched_all and answered_all:
            completed_modules += 1

    return {
        "user_id": user.id,
        "coins": total_coins,
        "total_modules": total_modules,
        "completed_modules": completed_modules,
        "videos_watched": videos_watched,
        "tests_answered": tests_answered,
        "tests_correct": tests_correct,
    }

class AnswerRequest(BaseModel):
    test_id: int
    selected_option_id: int

class AnswerResponse(BaseModel):
    is_correct: bool
    earned_coins: int
    total_user_coins: int

@router.post("/answer", response_model=AnswerResponse)
def answer_question(
    body: AnswerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1️⃣ Fetch the test
    test = db.query(Test).filter(Test.id == body.test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    # 2️⃣ Fetch the selected option
    option = db.query(Option).filter(Option.id == body.selected_option_id, Option.test_id == test.id).first()
    if not option:
        raise HTTPException(status_code=400, detail="Invalid option for this test")

    # 3️⃣ Check correctness
    is_correct = (option.id == test.correct_option_id)
    earned = test.coins if is_correct else 0

    # 4️⃣ Save progress (avoid duplicate submissions)
    existing = db.query(UserTestProgress).filter_by(
        user_id=current_user.id, test_id=test.id
    ).first()

    if existing:
        # already answered → don’t double-reward
        return AnswerResponse(
            is_correct=existing.is_correct,
            earned_coins=existing.earned_coins,
            total_user_coins=current_user.coins
        )

    progress = UserTestProgress(
        user_id=current_user.id,
        test_id=test.id,
        selected_option_id=option.id,
        is_correct=is_correct,
        earned_coins=earned
    )
    db.add(progress)

    # 5️⃣ Update user coins if correct
    if is_correct:
        current_user.coins += earned

    db.commit()
    db.refresh(current_user)

    return AnswerResponse(
        is_correct=is_correct,
        earned_coins=earned,
        total_user_coins=current_user.coins
    )












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
