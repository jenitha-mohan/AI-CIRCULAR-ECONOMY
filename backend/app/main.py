"""
AI Circular Economy Marketplace — Main FastAPI Application
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.app.config import settings
from backend.app.database import engine, Base, SessionLocal
from backend.app.services.seed_service import seed_database

# Routers
from backend.app.api.auth import router as auth_router
from backend.app.api.users import router as users_router
from backend.app.api.materials import router as materials_router
from backend.app.api.listings import router as listings_router
from backend.app.api.buyers import router as buyers_router
from backend.app.api.transactions import router as transactions_router
from backend.app.api.ml import router as ml_router
from backend.app.api.recommendations import router as recommendations_router
from backend.app.api.analytics import router as analytics_router

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("circular_economy")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing AI Circular Economy Database Schema...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    logger.info("System Ready.")
    yield
    logger.info("Shutting down platform services.")


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered circular economy marketplace connecting waste generators, recyclers, and buyers with computer vision material classification, ML price regression, and intelligent geospatial matchmaking.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static Uploads and Reports Mount
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.REPORTS_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
app.mount("/reports", StaticFiles(directory=settings.REPORTS_DIR), name="reports")

# Include API Routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(materials_router)
app.include_router(listings_router)
app.include_router(buyers_router)
app.include_router(transactions_router)
app.include_router(ml_router)
app.include_router(recommendations_router)
app.include_router(analytics_router)


# Global Exception Handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.detail}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    msg = errors[0]["msg"] if errors else "Validation error"
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"success": False, "message": f"Invalid input: {msg}", "errors": errors}
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"success": False, "message": "An unexpected server error occurred."}
    )


@app.get("/")
def root_status():
    return {
        "service": settings.APP_NAME,
        "status": "operational",
        "version": "1.0.0",
        "ml_mode": settings.ML_MODE,
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
