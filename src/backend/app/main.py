"""
FastAPI Application Entry Point
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import close_db, init_db

# Configure logging
logging.basicConfig(level=logging.INFO if settings.DEBUG else logging.WARNING)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown."""
    # Startup
    logger.info("Starting up Smart Attendance System API")
    # TODO: Enable database initialization after fixing UUID issues
    # await init_db()
    logger.info("Database initialization skipped for MVP")

    yield

    # Shutdown
    logger.info("Shutting down Smart Attendance System API")
    # await close_db()
    logger.info("Application shutdown complete")


app = FastAPI(
    title="Smart Attendance System API",
    description="智能簽到系統 API",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return {
        "status": "error",
        "message": "Internal server error",
        "detail": str(exc) if settings.DEBUG else "An unexpected error occurred"
    }


# Include API v1 router
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Smart Attendance System API",
        "version": "0.1.0"
    }


@app.get("/api/v1/health")
async def health_check():
    """API v1 health check"""
    return {
        "status": "ok",
        "version": "v1"
    }
