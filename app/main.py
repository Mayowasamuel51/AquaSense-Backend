




from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routers import health, auth  , learning# 👈 import your auth router
from .database import engine
from . import models
from mangum import Mangum


origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")]

models.Base.metadata.create_all(bind=engine)
app = FastAPI(title="Platform API", version="0.1.0")

# middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# routers

app.include_router(auth.router, prefix="/api/v1")# 👈 no need to add /auth again
app.include_router(learning.router, prefix="/api/v1")
