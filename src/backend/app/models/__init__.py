"""
SQLAlchemy models package.

All models inherit from Base and use mixins for common functionality.
Models are organized by bounded context (DDD):
- auth: User management
- calendar: Event scheduling
- attendance: Attendance tracking, leave/makeup requests

Import all models here to ensure relationships are properly configured.
"""

from app.models.base import Base
from app.models.enums import (
    AttendanceStatus,
    LeaveType,
    RequestStatus,
    UserRole,
)

# Import all models to register them with SQLAlchemy
from app.models.auth import User
from app.models.calendar import Event
from app.models.attendance import Attendance, LeaveRequest, MakeupRequest

__all__ = [
    # Base
    "Base",
    # Enums
    "UserRole",
    "AttendanceStatus",
    "LeaveType",
    "RequestStatus",
    # Models
    "User",
    "Event",
    "Attendance",
    "LeaveRequest",
    "MakeupRequest",
]
