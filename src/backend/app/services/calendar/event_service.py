"""
Event service for handling event creation and management.

Design Philosophy:
- Service layer for event management business logic
- Participant invitation and notification coordination
- Integration with Google Calendar (future)
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.calendar.event import Event
from app.models.calendar.event_participant import EventParticipant
from app.models.auth.user import User


class EventService:
    """Service for event management and participant coordination."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_event_with_participants(
        self,
        title: str,
        start_time: datetime,
        end_time: datetime,
        created_by: int,
        participant_ids: List[int],
        description: Optional[str] = None,
        grace_period_minutes: int = 5,
        google_event_id: Optional[str] = None
    ) -> Event:
        """Create a new event with participants.

        Args:
            title: Event title
            start_time: Event start time
            end_time: Event end time
            created_by: Creator user ID
            participant_ids: List of user IDs to invite
            description: Optional event description
            grace_period_minutes: Late check-in grace period (default: 5)
            google_event_id: Optional Google Calendar event ID

        Returns:
            Created event with participants

        Raises:
            ValueError: If end_time <= start_time or invalid participants
        """
        # Validate time range
        if end_time <= start_time:
            raise ValueError("End time must be after start time")

        # Generate google_event_id if not provided
        if not google_event_id:
            google_event_id = f"manual_{int(datetime.utcnow().timestamp())}_{created_by}"

        # Create event
        event = Event(
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            grace_period_minutes=grace_period_minutes,
            google_event_id=google_event_id,
            created_by=created_by
        )
        self.db.add(event)
        await self.db.flush()  # Get event ID

        # Add participants
        if participant_ids:
            await self._add_participants(event.id, participant_ids)

        await self.db.commit()
        await self.db.refresh(event)

        return event

    async def _add_participants(
        self,
        event_id: int,
        participant_ids: List[int]
    ) -> List[EventParticipant]:
        """Add participants to an event.

        Args:
            event_id: Event ID
            participant_ids: List of user IDs to invite

        Returns:
            List of created event participants

        Raises:
            ValueError: If any user IDs are invalid
        """
        # Remove duplicates
        unique_participant_ids = list(set(participant_ids))

        # Validate all users exist
        from sqlalchemy import select
        result = await self.db.execute(
            select(User).where(User.id.in_(unique_participant_ids))
        )
        existing_users = result.scalars().all()
        existing_user_ids = {user.id for user in existing_users}

        invalid_ids = set(unique_participant_ids) - existing_user_ids
        if invalid_ids:
            raise ValueError(f"Invalid user IDs: {invalid_ids}")

        # Create participant records
        participants = []
        for user_id in unique_participant_ids:
            participant = EventParticipant(
                event_id=event_id,
                user_id=user_id,
                invited_at=datetime.utcnow(),
                notification_sent=False
            )
            self.db.add(participant)
            participants.append(participant)

        return participants

    async def get_event_participants(
        self,
        event_id: int
    ) -> List[EventParticipant]:
        """Get all participants for an event.

        Args:
            event_id: Event ID

        Returns:
            List of event participants
        """
        from sqlalchemy import select
        result = await self.db.execute(
            select(EventParticipant)
            .where(EventParticipant.event_id == event_id)
            .order_by(EventParticipant.invited_at)
        )
        return list(result.scalars().all())

    async def get_user_invited_events(
        self,
        user_id: int,
        upcoming_only: bool = True
    ) -> List[Event]:
        """Get events a user is invited to.

        Args:
            user_id: User ID
            upcoming_only: If True, only return future events

        Returns:
            List of events
        """
        from sqlalchemy import select
        query = (
            select(Event)
            .join(EventParticipant, Event.id == EventParticipant.event_id)
            .where(EventParticipant.user_id == user_id)
        )

        if upcoming_only:
            query = query.where(Event.start_time > datetime.utcnow())

        query = query.order_by(Event.start_time)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def mark_notifications_sent(
        self,
        event_id: int
    ) -> None:
        """Mark all participants' notifications as sent.

        Args:
            event_id: Event ID
        """
        from sqlalchemy import update
        await self.db.execute(
            update(EventParticipant)
            .where(EventParticipant.event_id == event_id)
            .values(notification_sent=True)
        )
        await self.db.commit()
