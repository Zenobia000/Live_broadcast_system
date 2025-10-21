"""
Event repository for database operations.

Design Philosophy:
- Repository pattern for data access
- Clean interface for event operations
- Support for Google Calendar sync operations
"""

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.calendar.event import Event


class EventRepository:
    """Repository for Event model database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        title: str,
        start_time: datetime,
        end_time: datetime,
        google_event_id: str,
        description: Optional[str] = None,
        created_by: Optional[UUID] = None,
        grace_period_minutes: int = 5
    ) -> Event:
        """Create a new event."""
        event = Event(
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            google_event_id=google_event_id,
            created_by=created_by,
            grace_period_minutes=grace_period_minutes
        )
        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(event)
        return event

    async def get_by_id(self, event_id: int) -> Optional[Event]:
        """Get event by ID."""
        result = await self.session.execute(
            select(Event).where(Event.id == event_id)
        )
        return result.scalar_one_or_none()

    async def get_by_google_id(self, google_event_id: str) -> Optional[Event]:
        """Get event by Google Calendar event ID."""
        result = await self.session.execute(
            select(Event).where(Event.google_event_id == google_event_id)
        )
        return result.scalar_one_or_none()

    async def list_events(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 50
    ) -> List[Event]:
        """List events within time range."""
        query = select(Event).order_by(Event.start_time)

        if start_time:
            query = query.where(Event.start_time >= start_time)
        if end_time:
            query = query.where(Event.end_time <= end_time)

        query = query.limit(limit)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def list_upcoming_events(
        self,
        current_time: Optional[datetime] = None,
        hours_ahead: int = 24
    ) -> List[Event]:
        """List upcoming events."""
        if current_time is None:
            current_time = datetime.utcnow()

        end_time = current_time + timedelta(hours=hours_ahead)

        query = select(Event).where(
            Event.start_time >= current_time,
            Event.start_time <= end_time
        ).order_by(Event.start_time)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def list_ongoing_events(
        self,
        current_time: Optional[datetime] = None
    ) -> List[Event]:
        """List currently ongoing events."""
        if current_time is None:
            current_time = datetime.utcnow()

        query = select(Event).where(
            Event.start_time <= current_time,
            Event.end_time >= current_time
        ).order_by(Event.start_time)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def update(self, event: Event) -> Event:
        """Update event information."""
        await self.session.commit()
        await self.session.refresh(event)
        return event

    async def delete(self, event: Event) -> None:
        """Delete event."""
        await self.session.delete(event)
        await self.session.commit()

    async def exists_by_google_id(self, google_event_id: str) -> bool:
        """Check if event exists by Google Calendar ID."""
        result = await self.session.execute(
            select(Event.id).where(Event.google_event_id == google_event_id)
        )
        return result.scalar_one_or_none() is not None