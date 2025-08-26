SECRET_KEY = "your-secret-key-here"  # change in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 120
DATABASE_URL = "sqlite:///./test.db"
from pydantic import BaseModel
import os
class Settings(BaseModel):
    APP_ENV: str = os.getenv("APP_ENV", "dev")
    DATABASE_URL: str = os.getenv("DATABASE_URL","mysql+pymysql://apimypr5_mypromosphere:mypromosphere@131.153.147.186:3306/apimypr5_AquaSenseBackend")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-secret")
    JWT_REFRESH_SECRET: str = os.getenv("JWT_REFRESH_SECRET", "dev-refresh")
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:5174")

settings = Settings()