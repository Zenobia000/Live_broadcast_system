"""
Attendance service dependencies for FastAPI.

Design Philosophy (Linus's "Good Taste"):
- Clean dependency injection
- Single responsibility per service
- Proper session management
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.repositories.attendance.attendance_repository import AttendanceRepository
from app.repositories.calendar.event_repository import EventRepository
from app.services.attendance.attendance_service import AttendanceService


async def get_attendance_service(
    session: AsyncSession = Depends(get_session)
) -> AttendanceService:
    """Get attendance service instance with proper dependency injection."""
    attendance_repository = AttendanceRepository(session)
    event_repository = EventRepository(session)

    return AttendanceService(attendance_repository, event_repository)


# Type alias for easy import
AttendanceServiceDep = Annotated[AttendanceService, Depends(get_attendance_service)]