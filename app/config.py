import os
from pydantic import BaseModel



# IMGBB_API_KEY="b250634f93da9f6857fcf390924230c4"

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 120
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://apimypr5_mypromosphere:mypromosphere@131.153.147.186:3306/apimypr5_AquaSenseBackend"
)

# ==========================
# 🌍 Pydantic Settings Model
# ==========================
class Settings(BaseModel):
    APP_ENV: str = os.getenv("APP_ENV", "dev")
    DATABASE_URL: str = DATABASE_URL
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-secret")
    JWT_REFRESH_SECRET: str = os.getenv("JWT_REFRESH_SECRET", "dev-refresh")
    CORS_ORIGINS: str = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://localhost:5174"
    )

settings = Settings()

# ==========================
# ☁️ Cloudinary Configuration
# ==========================





# from dotenv import load_dotenv
# load_dotenv()
# import cloudinary
# from cloudinary import CloudinaryImage
# import cloudinary.uploader
# import cloudinary.api
#
# # Import to format the JSON responses
# # ==============================
# import json
#
# # Set configuration parameter: return "https" URLs by setting secure=True
# # ==============================
# config = cloudinary.config(secure=True)
#
# SECRET_KEY = "your-secret-key-here"  # change in production
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 120
# DATABASE_URL = "sqlite:///./test.db"
# from pydantic import BaseModel
# import os
# class Settings(BaseModel):
#     APP_ENV: str = os.getenv("APP_ENV", "dev")
#     DATABASE_URL: str = os.getenv("DATABASE_URL","mysql+pymysql://apimypr5_mypromosphere:mypromosphere@131.153.147.186:3306/apimypr5_AquaSenseBackend")
#     REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
#     JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-secret")
#     JWT_REFRESH_SECRET: str = os.getenv("JWT_REFRESH_SECRET", "dev-refresh")
#     CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:5174")
#
# settings = Settings()
#
#
#
# load_dotenv()
#
# cloudinary.config(
#     cloud_name=os.getenv("dicz9c7kk"),
#     api_key=os.getenv("948636269897915"),
#     api_secret=os.getenv("f87ZL-_tSg7eV__mVGrmOKtl-Rw"),
#     secure=True
# )
# #
# # VITE_CLOUDINARY_IMAGE_URL = "https://api.cloudinary.com/v1_1/dicz9c7kk/image/upload"
# #
# # VITE_CLOUDINARY_VIDEO_URL = "https://api.cloudinary.com/v1_1/dicz9c7kk/video/upload"
# #
# # VITE_CLOUDINARY_ADS_UPLOAD_PRESET = "mypromosphere"
# #
# # VITE_CLOUDINARY_CLOUD_NAME = "dicz9c7kk"
