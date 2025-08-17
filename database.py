from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# from config import DATABASE_URL
DATABASE_URL = "mysql+pymysql://apimypr5_mypromosphere:mypromosphere@131.153.147.186:3306/apimypr5_mypromosphere"
# DATABASE_URL = "mysql+pymysql://apimypr5_mypromosphere:mypromosphere@db.yourhost.com:3306/fastapi_db"
# DATABASE_URL = "mysql+pymysql://apimypr5_mypromosphere:mypromosphere@apimypr5_AquaSenseBackend:3306/fastapi_db"
engine = create_engine(DATABASE_URL)
# engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
