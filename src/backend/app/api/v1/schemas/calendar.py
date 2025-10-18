"""
Calendar-related Pydantic schemas for API requests and responses.

Design Philosophy:
- Clear separation between request and response schemas
- Type-safe data validation
- Self-documenting API contracts
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class CalendarEventBase(BaseModel):
    """Base schema for calendar events."""

    id: str = Field(..., description="Google Calendar event ID")
    title: str = Field(..., description="Event title/summary")
    description: Optional[str] = Field(None, description="Event description")
    start_time: str = Field(..., description="Event start time (ISO 8601)")
    end_time: str = Field(..., description="Event end time (ISO 8601)")


class CalendarEventResponse(CalendarEventBase):
    """Response schema for calendar events."""

    creator: Optional[dict] = Field(None, description="Event creator information")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "abc123def456",
                "title": "Team Stand-up Meeting",
                "description": "Daily team sync",
                "start_time": "2025-10-18T09:00:00Z",
                "end_time": "2025-10-18T09:30:00Z",
                "creator": {
                    "email": "user@example.com",
                    "displayName": "John Doe"
                }
            }
        }


class CalendarEventListResponse(BaseModel):
    """Response schema for list of calendar events."""

    events: List[CalendarEventResponse] = Field(
        ..., description="List of calendar events"
    )
    total: int = Field(..., description="Total number of events")

    class Config:
        json_schema_extra = {
            "example": {
                "events": [
                    {
                        "id": "abc123",
                        "title": "Morning Meeting",
                        "description": "Daily standup",
                        "start_time": "2025-10-18T09:00:00Z",
                        "end_time": "2025-10-18T09:30:00Z",
                        "creator": {"email": "manager@example.com"}
                    }
                ],
                "total": 1
            }
        }


class CheckInStatusResponse(BaseModel):
    """Response schema for check-in status."""

    should_check_in: bool = Field(
        ..., description="Whether user should check in now"
    )
    current_event: Optional[CalendarEventResponse] = Field(
        None, description="Current event if user should be attending"
    )
    message: str = Field(..., description="Status message")

    class Config:
        json_schema_extra = {
            "example": {
                "should_check_in": True,
                "current_event": {
                    "id": "xyz789",
                    "title": "Project Review",
                    "start_time": "2025-10-18T14:00:00Z",
                    "end_time": "2025-10-18T15:00:00Z"
                },
                "message": "You should be in 'Project Review' right now"
            }
        }


class CalendarSyncResponse(BaseModel):
    """Response schema for calendar synchronization."""

    success: bool = Field(..., description="Whether sync was successful")
    synced_events: int = Field(..., description="Number of events synced")
    message: str = Field(..., description="Sync status message")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "synced_events": 5,
                "message": "Successfully synced 5 events from Google Calendar"
            }
        }


class CalendarErrorResponse(BaseModel):
    """Error response schema for calendar operations."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "TokenExpired",
                "message": "Calendar access token has expired",
                "detail": "Please re-authenticate to grant Calendar permissions"
            }
        }
