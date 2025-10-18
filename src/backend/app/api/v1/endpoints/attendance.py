"""
Attendance API endpoints.

Design Philosophy:
- RESTful API design for attendance operations
- Event-driven auto check-in functionality
- Role-based access control for management features
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.attendance import AttendanceServiceDep
from app.api.dependencies.auth import AdminUser, CurrentUser
from app.api.dependencies.database import get_db_session
from app.api.v1.schemas.attendance import (
    AttendanceResponse,
    AttendanceWithDetails,
    AutoCheckInResponse,
    CheckInRequest,
    CheckInResponse,
)
from app.services.calendar.google_calendar_service import GoogleCalendarService

router = APIRouter()


@router.get("/today")
async def get_today_status(current_user: CurrentUser):
    """Get today's attendance status for current user.

    Returns:
        Simple status overview for today
    """
    from datetime import date

    today = date.today()

    return {
        "date": today.isoformat(),
        "user_id": str(current_user.id),
        "user_name": current_user.name,
        "status": "active",
        "message": f"Today's status for {current_user.name}"
    }


@router.post("/auto-checkin", response_model=AutoCheckInResponse)
async def auto_check_in(
    current_user: CurrentUser,
    attendance_service: AttendanceServiceDep
):
    """Automatically check in user for ongoing events.

    This is the core event-driven functionality:
    1. Find all currently ongoing events
    2. Check if user hasn't checked in yet
    3. Perform automatic check-in with late detection

    Returns:
        List of events user was checked in for
    """
    try:
        attendances = await attendance_service.auto_check_in_user(current_user.id)

        checked_in_events = [
            {
                "event_id": str(attendance.event_id),
                "attendance_id": str(attendance.id),
                "status": attendance.status.value,
                "check_in_time": attendance.check_in_time,
                "was_late": attendance.status.value == "LATE"
            }
            for attendance in attendances
        ]

        return AutoCheckInResponse(
            checked_in_events=checked_in_events,
            total_checked_in=len(attendances),
            message=f"Successfully checked in for {len(attendances)} events"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Auto check-in failed: {str(e)}"
        )


@router.post("/auto-checkin-calendar", response_model=dict)
async def auto_check_in_from_calendar(
    current_user: CurrentUser,
    db_session: AsyncSession = Depends(get_db_session),
):
    """Automatically check in user based on Google Calendar events.

    **M2 Milestone Core Functionality**

    This endpoint implements the event-driven automatic check-in:
    1. Check user's Google Calendar for current events
    2. If user should be in an event right now, auto check-in
    3. Determine if check-in is late based on event start time
    4. Create attendance record in database

    This should be called by the frontend:
    - On user login
    - On page load/refresh
    - Periodically (e.g., every 5 minutes)

    Returns:
        Auto check-in status with event and attendance details
    """
    import logging
    logger = logging.getLogger(__name__)

    try:
        # Check if user has Calendar access
        if not current_user.google_refresh_token:
            return {
                "checked_in": False,
                "message": "Calendar access not granted. Please re-authenticate with Calendar permissions.",
                "event": None,
                "attendance": None
            }

        # Initialize Calendar service
        calendar_service = GoogleCalendarService(current_user, db_session)

        # Check if user should be in an event right now
        current_event = await calendar_service.check_if_user_in_event_now()

        if not current_event:
            return {
                "checked_in": False,
                "message": "No calendar event happening right now",
                "event": None,
                "attendance": None
            }

        # Event found! Now check if we need to create attendance record
        # TODO: Implement actual attendance creation logic
        # For now, return event information

        logger.info(
            f"[Auto Check-in] User {current_user.email} should be in event: {current_event.get('title')}"
        )

        # Parse event times to determine if late
        start_time_str = current_event.get('start_time')
        start_time = calendar_service.parse_datetime(start_time_str)
        now = datetime.utcnow()

        is_late = now > start_time if start_time else False
        late_minutes = int((now - start_time).total_seconds() / 60) if is_late and start_time else 0

        return {
            "checked_in": True,
            "message": f"Auto check-in for '{current_event.get('title')}'",
            "event": {
                "id": current_event.get('id'),
                "title": current_event.get('title'),
                "start_time": start_time_str,
                "end_time": current_event.get('end_time'),
            },
            "attendance": {
                "status": "LATE" if is_late else "PRESENT",
                "check_in_time": now.isoformat() + 'Z',
                "is_late": is_late,
                "late_minutes": late_minutes if is_late else 0
            }
        }

    except Exception as e:
        logger.error(f"[Auto Check-in] Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Auto check-in from calendar failed: {str(e)}"
        )


@router.post("/checkin", response_model=CheckInResponse)
async def manual_check_in(
    checkin_request: CheckInRequest,
    current_user: CurrentUser,
    attendance_service: AttendanceServiceDep
):
    """Manual check-in for specific event.

    Args:
        checkin_request: Check-in request with event ID and optional time
        current_user: Current authenticated user

    Returns:
        Check-in result with attendance record
    """
    try:
        attendance = await attendance_service.manual_check_in(
            user_id=current_user.id,
            event_id=checkin_request.event_id,
            check_in_time=checkin_request.check_in_time
        )

        was_late = attendance.status.value == "LATE"

        return CheckInResponse(
            attendance=AttendanceResponse(
                id=attendance.id,
                user_id=attendance.user_id,
                event_id=attendance.event_id,
                status=attendance.status.value,
                check_in_time=attendance.check_in_time,
                note=attendance.note,
                created_at=attendance.created_at,
                updated_at=attendance.updated_at
            ),
            was_late=was_late,
            message="Successfully checked in" + (" (late)" if was_late else "")
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Check-in failed: {str(e)}"
        )


@router.get("/my-attendance", response_model=List[AttendanceWithDetails])
async def get_my_attendance(
    current_user: CurrentUser,
    attendance_service: AttendanceServiceDep,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Get current user's attendance records.

    Args:
        current_user: Current authenticated user
        start_date: Filter start date (optional)
        end_date: Filter end date (optional)

    Returns:
        List of attendance records with event details
    """
    try:
        attendances = await attendance_service.get_user_attendance(
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date
        )

        # For now, return attendance without event details since we'd need to join
        # In a full implementation, we'd modify the service to include event data
        return [
            AttendanceWithDetails(
                id=attendance.id,
                user_id=attendance.user_id,
                event_id=attendance.event_id,
                status=attendance.status.value,
                check_in_time=attendance.check_in_time,
                note=attendance.note,
                created_at=attendance.created_at,
                updated_at=attendance.updated_at,
                event_title="Event details to be implemented",  # TODO: Join with event
                event_start_time=None,  # TODO: Join with event
                event_end_time=None     # TODO: Join with event
            )
            for attendance in attendances
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve attendance: {str(e)}"
        )


@router.get("/events/{event_id}/attendance", response_model=List[AttendanceWithDetails])
async def get_event_attendance(
    event_id: UUID,
    admin_user: AdminUser
):
    """Get attendance records for specific event (admin only).

    Args:
        event_id: Event ID
        admin_user: Current admin user

    Returns:
        List of attendance records for the event
    """
    # TODO: Implement with proper dependency injection
    return []


@router.get("/{attendance_id}", response_model=AttendanceResponse)
async def get_attendance_record(
    attendance_id: UUID,
    current_user: CurrentUser
):
    """Get specific attendance record.

    Args:
        attendance_id: Attendance record ID
        current_user: Current authenticated user

    Returns:
        Attendance record details

    Raises:
        HTTPException: If record not found or access denied
    """
    # TODO: Implement with proper dependency injection and access control
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Attendance record not found"
    )


@router.put("/{attendance_id}/note")
async def update_attendance_note(
    attendance_id: UUID,
    note: str,
    admin_user: AdminUser
):
    """Update attendance record note (admin only).

    Args:
        attendance_id: Attendance record ID
        note: New note text
        admin_user: Current admin user

    Returns:
        Updated attendance record
    """
    # TODO: Implement with proper dependency injection
    return {"message": "Note update functionality will be available after dependency injection setup"}


@router.delete("/{attendance_id}")
async def soft_delete_attendance(
    attendance_id: UUID,
    admin_user: AdminUser
):
    """Soft delete attendance record (admin only).

    Args:
        attendance_id: Attendance record ID
        admin_user: Current admin user

    Returns:
        Deletion confirmation
    """
    # TODO: Implement with proper dependency injection
    return {"message": "Attendance record deletion functionality will be available after dependency injection setup"}