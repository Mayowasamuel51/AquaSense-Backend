from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import User

def delete_all_users():
    db: Session = SessionLocal()
    try:
        db.query(User).delete()
        db.commit()
        print("✅ All users deleted successfully.")
    except Exception as e:
        db.rollback()
        print("❌ Error:", e)
    finally:
        db.close()

delete_all_users()
