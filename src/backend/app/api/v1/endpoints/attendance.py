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
from app.core.database import get_session as get_db_session
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
async def get_today_status(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db_session)
):
    """Get today's attendance status for current user.

    Returns:
        Today's attendance status with check-in information
    """
    from datetime import date, datetime, time
    from app.models.attendance.attendance import Attendance
    from app.models.calendar.event import Event
    from sqlalchemy import select, and_

    today = date.today()

    # Get today's attendance records
    today_start = datetime.combine(today, time.min)
    today_end = datetime.combine(today, time.max)

    query = (
        select(Attendance, Event)
        .join(Event, Attendance.event_id == Event.id)
        .where(
            and_(
                Attendance.user_id == current_user.id,
                Event.start_time >= today_start,
                Event.start_time <= today_end
            )
        )
        .order_by(Event.start_time.desc())
        .limit(1)
    )

    result = await db.execute(query)
    attendance_with_event = result.first()

    if attendance_with_event:
        attendance, event = attendance_with_event
        return {
            "isCheckedIn": True,
            "checkInTime": attendance.check_in_time.strftime("%H:%M") if attendance.check_in_time else None,
            "eventTitle": event.title,
            "nextEventTime": None,
            "status": "late" if attendance.status.value == "late" else "present"
        }

    # No check-in today, find next event
    next_event_query = (
        select(Event)
        .where(
            and_(
                Event.creator_id == current_user.id,
                Event.start_time > datetime.now()
            )
        )
        .order_by(Event.start_time.asc())
        .limit(1)
    )

    next_result = await db.execute(next_event_query)
    next_event = next_result.scalar_one_or_none()

    return {
        "isCheckedIn": False,
        "checkInTime": None,
        "eventTitle": None,
        "nextEventTime": next_event.start_time.strftime("%H:%M") if next_event else None,
        "status": "waiting"
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
    attendance_service: AttendanceServiceDep,
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

        logger.info(
            f"[Auto Check-in] User {current_user.email} should be in event: {current_event.get('title')}"
        )

        # Create attendance record
        attendance = await attendance_service.check_in_from_calendar_event(
            user_id=current_user.id,
            calendar_event=current_event,
            check_in_time=datetime.utcnow()
        )

        # Calculate late minutes if late
        start_time = calendar_service.parse_datetime(current_event.get('start_time'))
        late_minutes = 0
        if attendance.status.value == "LATE" and start_time and attendance.check_in_time:
            late_minutes = int((attendance.check_in_time - start_time).total_seconds() / 60)

        return {
            "checked_in": True,
            "message": f"Successfully checked in for '{current_event.get('title')}'",
            "event": {
                "id": current_event.get('id'),
                "title": current_event.get('title'),
                "start_time": current_event.get('start_time'),
                "end_time": current_event.get('end_time'),
            },
            "attendance": {
                "id": str(attendance.id),
                "status": attendance.status.value,
                "check_in_time": attendance.check_in_time.isoformat() if attendance.check_in_time else None,
                "is_late": attendance.status.value == "LATE",
                "late_minutes": late_minutes
            }
        }

    except ValueError as e:
        # Handle business logic errors (e.g., already checked in, event ended)
        logger.warning(f"[Auto Check-in] Validation error: {str(e)}")
        return {
            "checked_in": False,
            "message": str(e),
            "event": None,
            "attendance": None
        }
    except Exception as e:
        logger.error(f"[Auto Check-in] Error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Auto check-in from calendar failed: {str(e)}"
        )


@router.get("/history")
async def get_attendance_history(
    current_user: CurrentUser,
    limit: int = 10,
    db: AsyncSession = Depends(get_db_session)
):
    """Get attendance history for current user.

    Args:
        current_user: Current authenticated user
        limit: Number of records to return (default: 10, max: 100)
        db: Database session

    Returns:
        List of attendance records with event details
    """
    from app.models.attendance.attendance import Attendance
    from app.models.calendar.event import Event
    from sqlalchemy import select

    # Limit max to 100
    limit = min(limit, 100)

    query = (
        select(Attendance, Event)
        .join(Event, Attendance.event_id == Event.id)
        .where(Attendance.user_id == current_user.id)
        .order_by(Attendance.created_at.desc())
        .limit(limit)
    )

    result = await db.execute(query)
    records = result.all()

    return [
        {
            "id": str(attendance.id),
            "userId": str(attendance.user_id),
            "eventId": str(attendance.event_id),
            "eventTitle": event.title,
            "status": attendance.status.value.lower(),
            "checkedInAt": attendance.check_in_time.isoformat() if attendance.check_in_time else None,
            "createdAt": attendance.created_at.isoformat(),
            "updatedAt": attendance.updated_at.isoformat()
        }
        for attendance, event in records
    ]


@router.post("/checkin", response_model=CheckInResponse)
async def manual_check_in_with_event(
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


@router.get("/history")
async def get_attendance_history(
    current_user: CurrentUser,
    attendance_service: AttendanceServiceDep,
    limit: Optional[int] = 10,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Get current user's attendance history.

    Args:
        current_user: Current authenticated user
        limit: Maximum number of records to return (default 10)
        start_date: Filter start date (optional)
        end_date: Filter end date (optional)

    Returns:
        List of attendance records
    """
    try:
        attendances = await attendance_service.get_user_attendance(
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date
        )

        # Limit results
        limited_attendances = attendances[:limit] if limit else attendances

        # Return simplified response matching frontend expectations
        return {
            "success": True,
            "data": [
                {
                    "id": str(attendance.id),
                    "userId": str(attendance.user_id),
                    "eventId": str(attendance.event_id),
                    "eventTitle": "Event",  # TODO: Join with event table
                    "status": attendance.status.value.lower(),
                    "checkedInAt": attendance.check_in_time.isoformat() if attendance.check_in_time else None,
                    "createdAt": attendance.created_at.isoformat(),
                    "updatedAt": attendance.updated_at.isoformat()
                }
                for attendance in limited_attendances
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to retrieve attendance history: {str(e)}"
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