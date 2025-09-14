from fastapi import FastAPI,  Request
from fastapi.middleware.cors import CORSMiddleware
# from starlette.responses import JSONResponse
from fastapi.responses import JSONResponse

from .config import settings
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from .routers import health, auth , myfarm , profileupdate , learning , recording, batch , units
# expenses , profileupdate, myfarm, ponds)   # 👈 import your auth router
from .database import engine
from . import models
import logging
import traceback
# from apscheduler.schedulers.background import BackgroundScheduler
# from mangum import Mangum


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

# Configure logging (you can also configure file logging if needed)
logger = logging.getLogger("uvicorn.error")

class GlobalErrorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)

        # Validation errors (422)
        except RequestValidationError as exc:
            logger.warning(f"Validation error on {request.url}: {exc.errors()}")
            return JSONResponse(
                status_code=422,
                content={
                    "success": False,
                    "status_code": 422,
                    "error": "Validation Error",
                    "detail": exc.errors(),
                },
            )

        # HTTP errors (like 401 Unauthorized, 404 Not Found, etc.)
        except StarletteHTTPException as exc:
            logger.info(f"HTTP error {exc.status_code} on {request.url}: {exc.detail}")
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "success": False,
                    "status_code": exc.status_code,
                    "error": "HTTP Error",
                    "detail": exc.detail,
                },
            )

        # Catch-all for unexpected errors
        except Exception as exc:
            logger.error(f"Unexpected error on {request.url}: {exc}")
            logger.debug(traceback.format_exc())  # full traceback
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "status_code": 500,
                    "error": "Internal Server Error from the backend , application still in progress",
                    "detail": "An unexpected error occurred. Please try again later.",
                },
            )
app.add_middleware(GlobalErrorMiddleware)
# # routers

app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")# 👈 no need to add /auth again
app.include_router(learning.router, prefix="/api/v1")
# app.include_router(expenses.router, prefix="/api/v1")
app.include_router(profileupdate.router, prefix="/api/v1")
app.include_router(myfarm.router, prefix="/api/v1")
app.include_router(batch.router, prefix="/api/v1")
app.include_router(units.router, prefix="/api/v1")
# app.run_server(debug=True, port=8050, host='0.0.0.0')