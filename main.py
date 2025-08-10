from fastapi import FastAPI
from database import Base, engine
import models
from auth import router as auth_router
# from auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="User Auth API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the auth routes (prefix already defined in auth.py)
app.include_router(auth_router)
