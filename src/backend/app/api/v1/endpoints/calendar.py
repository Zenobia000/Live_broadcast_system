"""
Calendar API endpoints for Google Calendar integration.

Design Philosophy:
- RESTful API design
- Clear error handling
- Integration with GoogleCalendarService
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import CurrentUser
from app.api.dependencies.database import get_db_session
from app.api.v1.schemas.calendar import (
    CalendarErrorResponse,
    CalendarEventListResponse,
    CalendarEventResponse,
    CheckInStatusResponse,
)
from app.services.calendar.google_calendar_service import GoogleCalendarService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/events",
    response_model=CalendarEventListResponse,
    summary="List calendar events",
    description="Get user's Google Calendar events within a time range"
)
async def list_calendar_events(
    current_user: CurrentUser,
    db_session: AsyncSession = Depends(get_db_session),
    days_ahead: int = Query(7, ge=1, le=30, description="Number of days to look ahead"),
):
    """List user's calendar events.

    Args:
        current_user: Current authenticated user
        db_session: Database session
        days_ahead: Number of days to look ahead (1-30)

    Returns:
        List of calendar events

    Raises:
        HTTPException: If Calendar API access fails
    """
    try:
        # Check if user has Calendar access
        if not current_user.google_refresh_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Calendar access not granted. Please re-authenticate with Calendar permissions."
            )

        # Initialize Calendar service
        calendar_service = GoogleCalendarService(current_user, db_session)

        # Get events
        time_max = datetime.utcnow() + timedelta(days=days_ahead)
        events = await calendar_service.list_events(
            time_min=datetime.utcnow(),
            time_max=time_max,
            max_results=50
        )

        logger.info(f"[Calendar API] Retrieved {len(events)} events for user {current_user.email}")

        return CalendarEventListResponse(
            events=[CalendarEventResponse(**event) for event in events],
            total=len(events)
        )

    except Exception as e:
        logger.error(f"[Calendar API] Error listing events: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve calendar events: {str(e)}"
        )


@router.get(
    "/events/today",
    response_model=CalendarEventListResponse,
    summary="Get today's events",
    description="Get all events happening today"
)
async def get_today_events(
    current_user: CurrentUser,
    db_session: AsyncSession = Depends(get_db_session),
):
    """Get today's calendar events.

    Args:
        current_user: Current authenticated user
        db_session: Database session

    Returns:
        List of today's events

    Raises:
        HTTPException: If Calendar API access fails
    """
    try:
        if not current_user.google_refresh_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Calendar access not granted"
            )

        calendar_service = GoogleCalendarService(current_user, db_session)
        events = await calendar_service.get_upcoming_events_for_today()

        logger.info(f"[Calendar API] Retrieved {len(events)} events for today for user {current_user.email}")

        return CalendarEventListResponse(
            events=[CalendarEventResponse(**event) for event in events],
            total=len(events)
        )

    except Exception as e:
        logger.error(f"[Calendar API] Error getting today's events: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve today's events: {str(e)}"
        )


@router.get(
    "/check-in-status",
    response_model=CheckInStatusResponse,
    summary="Check if user should check in now",
    description="Determine if user should be checking into an event right now"
)
async def get_check_in_status(
    current_user: CurrentUser,
    db_session: AsyncSession = Depends(get_db_session),
):
    """Check if user should check in to an event now.

    This endpoint is crucial for automatic attendance tracking.
    It checks if there's a calendar event happening right now that
    the user should attend.

    Args:
        current_user: Current authenticated user
        db_session: Database session

    Returns:
        Check-in status with current event if applicable

    Raises:
        HTTPException: If Calendar API access fails
    """
    try:
        if not current_user.google_refresh_token:
            return CheckInStatusResponse(
                should_check_in=False,
                current_event=None,
                message="Calendar access not granted. Please re-authenticate."
            )

        calendar_service = GoogleCalendarService(current_user, db_session)
        current_event = await calendar_service.check_if_user_in_event_now()

        if current_event:
            logger.info(
                f"[Calendar API] User {current_user.email} should be in event: {current_event.get('title')}"
            )
            return CheckInStatusResponse(
                should_check_in=True,
                current_event=CalendarEventResponse(**current_event),
                message=f"You should be in '{current_event.get('title')}' right now"
            )
        else:
            return CheckInStatusResponse(
                should_check_in=False,
                current_event=None,
                message="No event happening right now"
            )

    except Exception as e:
        logger.error(f"[Calendar API] Error checking check-in status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check check-in status: {str(e)}"
        )


@router.get(
    "/events/{event_id}",
    response_model=CalendarEventResponse,
    summary="Get specific event",
    description="Get details of a specific calendar event"
)
async def get_calendar_event(
    event_id: str,
    current_user: CurrentUser,
    db_session: AsyncSession = Depends(get_db_session),
):
    """Get specific calendar event.

    Args:
        event_id: Google Calendar event ID
        current_user: Current authenticated user
        db_session: Database session

    Returns:
        Event details

    Raises:
        HTTPException: If event not found or Calendar API access fails
    """
    try:
        if not current_user.google_refresh_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Calendar access not granted"
            )

        calendar_service = GoogleCalendarService(current_user, db_session)
        event = await calendar_service.get_event(event_id)

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event {event_id} not found"
            )

        return CalendarEventResponse(**event)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Calendar API] Error getting event {event_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve event: {str(e)}"
        )
