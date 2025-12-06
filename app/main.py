import os
from fastapi import FastAPI,  Request
from fastapi.middleware.cors import CORSMiddleware
# from starlette.responses import JSONResponse
from fastapi.responses import JSONResponse
from starlette.responses import FileResponse
from .config import settings
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from .routers import(contact,
                     health,
                     auth,
                     myfarm,
                     profileupdate,
                     learning ,
                     questions,
                     vendor,
                     # categories,
                     # batch,
                     # units,
                     vendor_product,
                     vetsupport,
                     paystack,
                     address,
                     # products,
                     # dailyrecords,
                     # feeds, waitlist, income, stocking,
                     labs, agent, checkout,test , userimage ,batchinsight, admin, clusteradd,syncrouter)
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

# class GlobalErrorMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next):
#         try:
#             return await call_next(request)
#
#         # Validation errors (422)
#         except RequestValidationError as exc:
#             logger.warning(f"Validation error on {request.url}: {exc.errors()}")
#             return JSONResponse(
#                 status_code=422,
#                 content={
#                     "success": False,
#                     "status_code": 422,
#                     "error": "Validation Error",
#                     "detail": exc.errors(),
#                 },
#             )
#
#         # HTTP errors (like 401 Unauthorized, 404 Not Found, etc.)
#         except StarletteHTTPException as exc:
#             logger.info(f"HTTP error {exc.status_code} on {request.url}: {exc.detail}")
#             return JSONResponse(
#                 status_code=exc.status_code,
#                 content={
#                     "success": False,
#                     "status_code": exc.status_code,
#                     "error": "HTTP Error",
#                     "detail": exc.detail,
#                 },
#             )
#
#         # Catch-all for unexpected errors
#         except Exception as exc:
#             logger.error(f"Unexpected error on {request.url}: {exc}")
#             logger.debug(traceback.format_exc())  # full traceback
#             return JSONResponse(
#                 status_code=500,
#                 content={
#                     "success": False,
#                     "status_code": 500,
#                     "error": "Internal Server Error from the backend , application still in progress",
#                     "detail": "An unexpected error occurred. Please try again later.",
#                 },
#             )
# app.add_middleware(GlobalErrorMiddleware)
# # routers
# # ---------- CUSTOM VALIDATION HANDLER ----------
# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request: Request, exc: RequestValidationError):
#     errors = []
#     for err in exc.errors():
#         field = ".".join(str(loc) for loc in err["loc"] if loc not in ("body", "query", "path"))
#         errors.append({
#             "field": field,
#             "message": err["msg"]
#         })
#     return JSONResponse(
#         status_code=422,
#         content={"errors": errors}
#     )

class GlobalErrorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)

        # Validation errors (422)
        except RequestValidationError as exc:
            logger.warning(f"Validation error on {request.url}: {exc.errors()}")

            # take only first error message, or join multiple if needed
            first_error = exc.errors()[0]
            field = ".".join(str(loc) for loc in first_error["loc"] if loc not in ("body", "query", "path"))
            message = f"{field}: {first_error['msg']}" if field else first_error["msg"]

            return JSONResponse(
                status_code=422,
                content={
                    "success": False,
                    "status_code": 422,
                    "detail": message
                },
            )

        # HTTP errors (404, 401, etc.)
        except StarletteHTTPException as exc:
            logger.info(f"HTTP error {exc.status_code} on {request.url}: {exc.detail}")

            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "success": False,
                    "status_code": exc.status_code,
                    "detail": exc.detail
                },
            )

        # Unexpected / Crash errors (500)
        except Exception as exc:
            logger.error(f"Unexpected error on {request.url}: {exc}")
            logger.debug(traceback.format_exc())

            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "status_code": 500,
                    "detail": "An unexpected error occurred. Please try again later."
                },
            )
app.add_middleware(GlobalErrorMiddleware)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Pick the first error
    first_error = exc.errors()[0]
    field = ".".join(str(loc) for loc in first_error["loc"] if loc not in ("body", "query", "path"))
    message = f"{field}: {first_error['msg']}" if field else first_error["msg"]

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "status_code": 422,
            "detail": message
        }
    )


@app.get("/.well-known/assetlinks.json", response_class=FileResponse)
async def serve_assetlinks():
    # go one folder up from main.py to project root
    base_dir = os.path.dirname(os.path.dirname(__file__))
    file_path = os.path.join(base_dir, ".well-known", "assetlinks.json")
    return FileResponse(file_path, media_type="application/json")

app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")# 👈 no need to add /auth again
app.include_router(learning.router, prefix="/api/v1")
# app.include_router(products.router, prefix="/api/v1")
app.include_router(profileupdate.router, prefix="/api/v1")
app.include_router(myfarm.router, prefix="/api/v1")
# app.include_router(batch.router, prefix="/api/v1")
# app.include_router(units.router, prefix="/api/v1")
app.include_router(address.router, prefix="/api/v1")
# app.include_router(categories.router, prefix="/api/v1")
# app.include_router(dailyrecords.router,prefix="/api/v1")
app.include_router(address.router,prefix="/api/v1")
# (app.include_router(feeds.router,prefix="/api/v1" ))
app.include_router(contact.router,prefix="/api/v1" )
# app.include_router(waitlist.router,prefix="/api/v1" )
# app.include_router(income.router,prefix="/api/v1" )
# app.include_router(stocking.router,prefix="/api/v1" )
app.include_router(labs.router,prefix="/api/v1" )
app.include_router(agent.router,prefix="/api/v1" )
app.include_router(questions.router,prefix="/api/v1" )
app.include_router(checkout.router,prefix="/api/v1" )
app.include_router(test.router,prefix="/api/v1" )
app.include_router(vendor_product.router, prefix="/api/v1")
app.include_router(vendor.router,prefix="/api/v1" )
app.include_router(userimage.router,prefix="/api/v1" )
app.include_router(vetsupport.router,prefix="/api/v1" )
app.include_router(paystack.router,prefix="/api/v1" )
app.include_router(clusteradd.router,prefix="/api/v1" )
app.include_router(admin.router,prefix="/api/v1" )
app.include_router(batchinsight.router,prefix="/api/v1" )
app.include_router(syncrouter.router,prefix="/api/v1" )

# app.run_server(debug=True, port=8050, host='0.0.0.0')