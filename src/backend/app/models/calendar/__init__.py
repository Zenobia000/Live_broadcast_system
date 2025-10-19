"""Calendar models package."""

from app.models.calendar.event import Event
from app.models.calendar.event_participant import EventParticipant

__all__ = ["Event", "EventParticipant"]
