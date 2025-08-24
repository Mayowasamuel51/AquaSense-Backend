from passlib.hash import bcrypt
from models import User
from app.schemas import UserCreate, UserProfileUpdate
from sqlalchemy.orm import Session

def get_all_users(db: Session):
    return db.query(User).all()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    hashed_password = bcrypt.hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        gender=user.gender
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_profile(db: Session, user_id: int, profile: UserProfileUpdate):
    db_user = db.query(User).filter(User.id == user_id).first()
    for field, value in profile.dict(exclude_unset=True).items():
        setattr(db_user, field, value)
    # Auto-mark profile as completed if important fields are filled
    if db_user.first_name and db_user.last_name and db_user.gender:
        db_user.profile_completed = True
    db.commit()
    db.refresh(db_user)
    return db_user
