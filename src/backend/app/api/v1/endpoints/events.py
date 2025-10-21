"""
Events API endpoints.

Design Philosophy:
- RESTful API for event management
- Calendar synchronization endpoints
- Admin controls for event management
"""

from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from google.oauth2.credentials import Credentials

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import AdminUser, CurrentUser
from app.core.database import get_session as get_db_session
from app.api.v1.schemas.event import (
    EventCreate,
    EventResponse,
    EventSyncRequest,
    EventSyncResponse,
    EventUpdate,
    EventWithAttendance,
    UpcomingEventsResponse,
)
from app.services.calendar.event_service import EventService

router = APIRouter()


@router.get("/upcoming", response_model=UpcomingEventsResponse)
async def get_upcoming_events(
    current_user: CurrentUser,
    hours_ahead: int = 24
):
    """Get upcoming events.

    Args:
        hours_ahead: Number of hours to look ahead (default: 24)
        current_user: Current authenticated user

    Returns:
        List of upcoming events
    """
    # TODO: Implement with proper dependency injection
    return UpcomingEventsResponse(
        events=[],
        total_count=0,
        time_range_hours=hours_ahead
    )


@router.get("/ongoing", response_model=List[EventResponse])
async def get_ongoing_events(current_user: CurrentUser):
    """Get currently ongoing events.

    Args:
        current_user: Current authenticated user

    Returns:
        List of ongoing events
    """
    # TODO: Implement with proper dependency injection
    return []


@router.post("/sync", response_model=EventSyncResponse, dependencies=[Depends(AdminUser)])
async def sync_events_from_google(sync_request: EventSyncRequest):
    """Sync events from Google Calendar (admin only).

    Args:
        sync_request: Sync configuration

    Returns:
        Sync result with list of events
    """
    # TODO: Implement with proper Google Calendar credentials and dependency injection
    return EventSyncResponse(
        synced_events=[],
        total_synced=0,
        message="Calendar sync functionality will be available after Google API setup"
    )


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: int,
    current_user: CurrentUser
):
    """Get specific event details.

    Args:
        event_id: Event ID
        current_user: Current authenticated user

    Returns:
        Event details
    """
    # TODO: Implement with proper dependency injection
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Event not found"
    )


@router.get("/{event_id}/attendance", response_model=EventWithAttendance)
async def get_event_with_attendance(
    event_id: int,
    admin_user: AdminUser
):
    """Get event with attendance statistics (admin only).

    Args:
        event_id: Event ID
        admin_user: Current admin user

    Returns:
        Event details with attendance statistics
    """
    # TODO: Implement with proper dependency injection
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Event not found"
    )


@router.post("/", response_model=EventResponse)
async def create_manual_event(
    event_create: EventCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db_session)
):
    """Create manual event with participants.

    Args:
        event_create: Event creation data (includes participant_ids)
        current_user: Current authenticated user (any logged-in user can create events)
        db: Database session

    Returns:
        Created event

    Raises:
        HTTPException: If validation fails or participants are invalid
    """
    # All authenticated users can create events

    try:
        event_service = EventService(db)
        event = await event_service.create_event_with_participants(
            title=event_create.title,
            start_time=event_create.start_time,
            end_time=event_create.end_time,
            created_by=current_user.id,
            participant_ids=event_create.participant_ids,
            description=event_create.description,
            grace_period_minutes=event_create.grace_period_minutes,
            google_event_id=event_create.google_event_id
        )

        # TODO: Trigger notification service to send invitations to participants
        # This will be implemented in the next phase

        return EventResponse(
            id=event.id,
            title=event.title,
            description=event.description,
            start_time=event.start_time,
            end_time=event.end_time,
            grace_period_minutes=event.grace_period_minutes,
            google_event_id=event.google_event_id,
            created_by=event.created_by,
            created_at=event.created_at,
            updated_at=event.updated_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{event_id}", response_model=EventResponse, dependencies=[Depends(AdminUser)])
async def update_event(
    event_id: int,
    event_update: EventUpdate,
    admin_user: AdminUser
):
    """Update event details (admin only).

    Args:
        event_id: Event ID
        event_update: Event update data
        admin_user: Current admin user

    Returns:
        Updated event
    """
    # TODO: Implement with proper dependency injection
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Event not found"
    )


@router.delete("/{event_id}", dependencies=[Depends(AdminUser)])
async def delete_event(
    event_id: int,
    admin_user: AdminUser
):
    """Delete event (admin only).

    Args:
        event_id: Event ID
        admin_user: Current admin user

    Returns:
        Deletion confirmation
    """
    # TODO: Implement with proper dependency injection
    return {"message": "Event deletion functionality will be available after dependency injection setup"}


@router.get("/admin/attendance-overview")
async def get_attendance_overview(
    admin_user: AdminUser,
    db: AsyncSession = Depends(get_db_session),
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    limit: int = 50
):
    """Get attendance overview for all events (admin only).

    Returns event list with attendance statistics:
    - Expected attendees (participants)
    - Actually attended (checked in)
    - Not attended (absent)

    Args:
        admin_user: Current admin user
        db: Database session
        start_date: Filter events from this date (optional)
        end_date: Filter events to this date (optional)
        limit: Maximum number of events to return (default: 50)

    Returns:
        List of events with attendance breakdown
    """
    from datetime import timezone
    from sqlalchemy import select, func, case
    from sqlalchemy.orm import selectinload
    from app.models.calendar.event import Event
    from app.models.calendar.event_participant import EventParticipant
    from app.models.attendance.attendance import Attendance
    from app.models.auth.user import User
    from app.models.enums import AttendanceStatus

    # Build query for events
    query = select(Event).options(
        selectinload(Event.participants).selectinload(EventParticipant.user),
        selectinload(Event.attendances).selectinload(Attendance.user)
    )

    # Apply date filters if provided
    if start_date:
        query = query.where(Event.start_time >= start_date)
    if end_date:
        query = query.where(Event.start_time <= end_date)

    # Order by start time descending (newest first) and limit
    query = query.order_by(Event.start_time.desc()).limit(limit)

    result = await db.execute(query)
    events = result.scalars().all()

    # Build response with attendance statistics
    event_list = []
    for event in events:
        # Get all participants (expected attendees)
        participants = event.participants
        participant_ids = {p.user_id for p in participants}

        # Get attendance records
        attendances = event.attendances
        attendance_by_user = {a.user_id: a for a in attendances if not a.deleted_at}

        # Categorize users
        attended_users = []
        absent_users = []

        for participant in participants:
            user = participant.user
            attendance = attendance_by_user.get(user.id)

            user_info = {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "avatar_url": user.avatar_url
            }

            if attendance and attendance.is_present_or_late:
                # User checked in
                attended_users.append({
                    **user_info,
                    "status": attendance.status.value if hasattr(attendance.status, 'value') else str(attendance.status),
                    "check_in_time": attendance.check_in_time.isoformat() if attendance.check_in_time else None
                })
            else:
                # User did not check in (or has excused absence)
                status = "absent"
                if attendance:
                    status = attendance.status.value if hasattr(attendance.status, 'value') else str(attendance.status)

                absent_users.append({
                    **user_info,
                    "status": status
                })

        # Convert event times to Taipei timezone for display
        TAIPEI_TZ = timezone(timedelta(hours=8))
        start_taipei = event.start_time.astimezone(TAIPEI_TZ)
        end_taipei = event.end_time.astimezone(TAIPEI_TZ)

        event_list.append({
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "start_time": start_taipei.isoformat(),
            "end_time": end_taipei.isoformat(),
            "grace_period_minutes": event.grace_period_minutes,
            "statistics": {
                "expected_count": len(participants),
                "attended_count": len(attended_users),
                "absent_count": len(absent_users)
            },
            "attended_users": attended_users,
            "absent_users": absent_users
        })

    return {
        "success": True,
        "data": event_list,
        "total": len(event_list)
    }