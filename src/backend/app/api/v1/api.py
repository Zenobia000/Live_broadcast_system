"""
API v1 router configuration.

Aggregates all v1 API endpoints into a single router.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import attendance, auth, events, requests

api_router = APIRouter()

# Authentication endpoints
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"]
)

# Event management endpoints
api_router.include_router(
    events.router,
    prefix="/events",
    tags=["events"]
)

# Attendance endpoints
api_router.include_router(
    attendance.router,
    prefix="/attendance",
    tags=["attendance"]
)

# Leave and Makeup request endpoints
api_router.include_router(
    requests.router,
    prefix="/requests",
    tags=["requests"]
)