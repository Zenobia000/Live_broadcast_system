"""
Event Pydantic schemas for API input/output validation.

Design Philosophy:
- Comprehensive event information
- Support for calendar synchronization
- Clear event timing and attendance data
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class EventBase(BaseModel):
    """Base event schema."""

    title: str = Field(..., min_length=1, max_length=255, description="Event title")
    description: Optional[str] = Field(None, description="Event description")
    start_time: datetime = Field(..., description="Event start time")
    end_time: datetime = Field(..., description="Event end time")
    grace_period_minutes: int = Field(
        5,
        ge=0,
        le=60,
        description="Grace period for late check-in (0-60 minutes)"
    )


class EventCreate(EventBase):
    """Schema for creating a new event."""

    google_event_id: Optional[str] = Field(
        None,
        max_length=255,
        description="Google Calendar event ID (for synced events)"
    )
    participant_ids: List[int] = Field(
        default_factory=list,
        description="List of user IDs to invite to this event"
    )


class EventUpdate(BaseModel):
    """Schema for updating event information."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None)
    start_time: Optional[datetime] = Field(None)
    end_time: Optional[datetime] = Field(None)
    grace_period_minutes: Optional[int] = Field(None, ge=0, le=60)


class EventResponse(EventBase):
    """Schema for event API responses."""

    id: int = Field(..., description="Event ID")
    google_event_id: str = Field(..., description="Google Calendar event ID")
    created_by: Optional[int] = Field(None, description="Creator user ID")
    created_at: datetime = Field(..., description="Event creation time")
    updated_at: datetime = Field(..., description="Event last update time")

    class Config:
        from_attributes = True


class EventWithCreator(EventResponse):
    """Event response with creator information."""

    creator_name: Optional[str] = Field(None, description="Creator display name")
    creator_email: Optional[str] = Field(None, description="Creator email")


class EventWithAttendance(EventResponse):
    """Event response with attendance statistics."""

    total_attendees: int = Field(..., description="Total number of attendees")
    present_count: int = Field(..., description="Number of on-time attendees")
    late_count: int = Field(..., description="Number of late attendees")
    absent_count: int = Field(..., description="Number of absent attendees")
    leave_count: int = Field(..., description="Number of approved leaves")
    attendance_rate: float = Field(
        ...,
        description="Attendance rate ((present + late + leave) / total)"
    )


class EventSyncRequest(BaseModel):
    """Schema for calendar sync request."""

    calendar_id: str = Field("primary", description="Google Calendar ID")
    days_ahead: int = Field(
        30,
        ge=1,
        le=365,
        description="Number of days to sync ahead"
    )


class EventSyncResponse(BaseModel):
    """Schema for calendar sync response."""

    synced_events: List[EventResponse] = Field(..., description="List of synced events")
    total_synced: int = Field(..., description="Total number of events synced")
    message: str = Field(..., description="Sync result message")


class UpcomingEventsResponse(BaseModel):
    """Schema for upcoming events response."""

    events: List[EventResponse] = Field(..., description="List of upcoming events")
    total_count: int = Field(..., description="Total number of upcoming events")
    time_range_hours: int = Field(..., description="Time range in hours")