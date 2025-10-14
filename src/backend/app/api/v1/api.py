"""
API v1 router configuration.

Aggregates all v1 API endpoints into a single router.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth

api_router = APIRouter()

# Authentication endpoints
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"]
)