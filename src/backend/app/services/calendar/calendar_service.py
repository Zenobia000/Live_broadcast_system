"""
Calendar service for event management and synchronization.

Design Philosophy:
- High-level calendar operations
- Orchestrates Google Calendar API and local database
- Event-driven attendance creation
"""

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from google.oauth2.credentials import Credentials

from app.models.calendar.event import Event
from app.repositories.calendar.event_repository import EventRepository
from app.services.calendar.google_calendar_service import GoogleCalendarService


class CalendarService:
    """Calendar service for event management."""

    def __init__(
        self,
        event_repository: EventRepository,
        google_calendar_service: Optional[GoogleCalendarService] = None
    ):
        self.event_repository = event_repository
        self.google_calendar_service = google_calendar_service

    async def sync_events_from_google(
        self,
        credentials: Credentials,
        calendar_id: str = 'primary',
        days_ahead: int = 30
    ) -> List[Event]:
        """Sync events from Google Calendar.

        Args:
            credentials: Google OAuth credentials
            calendar_id: Google Calendar ID
            days_ahead: Number of days to sync ahead

        Returns:
            List of synced events

        Raises:
            Exception: If sync fails
        """
        # Initialize Google Calendar service with credentials
        google_service = GoogleCalendarService(credentials)

        # Fetch events from Google Calendar
        time_min = datetime.utcnow()
        time_max = time_min + timedelta(days=days_ahead)

        calendar_events = await google_service.list_events(
            calendar_id=calendar_id,
            time_min=time_min,
            time_max=time_max
        )

        # Sync to local database
        return await google_service.sync_events_to_database(
            calendar_events=calendar_events,
            event_repository=self.event_repository
        )

    async def get_event(self, event_id: UUID) -> Optional[Event]:
        """Get event by ID."""
        return await self.event_repository.get_by_id(event_id)

    async def list_upcoming_events(
        self,
        hours_ahead: int = 24
    ) -> List[Event]:
        """List upcoming events."""
        return await self.event_repository.list_upcoming_events(
            hours_ahead=hours_ahead
        )

    async def list_ongoing_events(self) -> List[Event]:
        """List currently ongoing events."""
        return await self.event_repository.list_ongoing_events()

    async def get_events_in_range(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> List[Event]:
        """Get events within time range."""
        return await self.event_repository.list_events(
            start_time=start_time,
            end_time=end_time
        )

    async def create_manual_event(
        self,
        title: str,
        start_time: datetime,
        end_time: datetime,
        created_by: UUID,
        description: Optional[str] = None,
        grace_period_minutes: int = 5
    ) -> Event:
        """Create a manual event (not synced from Google Calendar).

        Args:
            title: Event title
            start_time: Event start time
            end_time: Event end time
            created_by: User who created the event
            description: Event description
            grace_period_minutes: Late check-in grace period

        Returns:
            Created event

        Raises:
            ValueError: If event times are invalid
        """
        if end_time <= start_time:
            raise ValueError("End time must be after start time")

        # Generate a fake Google event ID for manual events
        google_event_id = f"manual_{datetime.utcnow().isoformat()}"

        return await self.event_repository.create(
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            google_event_id=google_event_id,
            created_by=created_by,
            grace_period_minutes=grace_period_minutes
        )