from fastapi.logger import logger
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
# from config import DATABASE_URL
DATABASE_URL = "mysql+pymysql://apimypr5_mypromosphere:mypromosphere@131.153.147.186:3306/apimypr5_AquaSenseBackend"
engine = create_engine(DATABASE_URL,
    pool_size=10,          # max connections in pool
    max_overflow=20,       # extra connections if pool is full
    pool_timeout=30,       # wait time before giving up
    pool_recycle=1800,
    pool_pre_ping=True,)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    logger.info("➡️ Open DB session")
    try:
        yield db
    finally:
        db.close()
        logger.info("✅ Closed DB session")
        #
        # def get_db():
        #     db = SessionLocal()
        #     try:
        #         yield db
        #     finally:
        #         db.close()