"""
Attendance Pydantic schemas for API input/output validation.

Design Philosophy:
- Clear request/response separation
- Comprehensive attendance information
- Support for attendance reporting
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import AttendanceStatus


class AttendanceBase(BaseModel):
    """Base attendance schema."""

    status: AttendanceStatus = Field(..., description="Attendance status")
    check_in_time: Optional[datetime] = Field(None, description="Check-in timestamp")
    note: Optional[str] = Field(None, description="Additional notes")


class AttendanceCreate(AttendanceBase):
    """Schema for creating attendance record."""

    user_id: int = Field(..., description="User ID")
    event_id: int = Field(..., description="Event ID")


class AttendanceUpdate(BaseModel):
    """Schema for updating attendance record."""

    status: Optional[AttendanceStatus] = Field(None, description="New attendance status")
    note: Optional[str] = Field(None, description="Updated notes")


class AttendanceResponse(AttendanceBase):
    """Schema for attendance API responses."""

    id: int = Field(..., description="Attendance record ID")
    user_id: int = Field(..., description="User ID")
    event_id: int = Field(..., description="Event ID")
    created_at: datetime = Field(..., description="Record creation time")
    updated_at: datetime = Field(..., description="Record last update time")

    class Config:
        from_attributes = True


class AttendanceWithDetails(AttendanceResponse):
    """Attendance response with user and event details."""

    user_name: Optional[str] = Field(None, description="User display name")
    user_email: Optional[str] = Field(None, description="User email")
    event_title: Optional[str] = Field(None, description="Event title")
    event_start_time: Optional[datetime] = Field(None, description="Event start time")
    event_end_time: Optional[datetime] = Field(None, description="Event end time")


class CheckInRequest(BaseModel):
    """Schema for manual check-in request."""

    event_id: int = Field(..., description="Event ID to check in for")
    check_in_time: Optional[datetime] = Field(
        None,
        description="Check-in time (default: current time)"
    )


class CheckInResponse(BaseModel):
    """Schema for check-in response."""

    attendance: AttendanceResponse = Field(..., description="Updated attendance record")
    was_late: bool = Field(..., description="Whether check-in was considered late")
    message: str = Field(..., description="Check-in result message")


class AutoCheckInResponse(BaseModel):
    """Schema for auto check-in response."""

    checked_in_events: List[AttendanceResponse] = Field(
        ...,
        description="List of events user was checked in for"
    )
    total_checked_in: int = Field(..., description="Number of events checked in")
    message: str = Field(..., description="Auto check-in result message")


class AttendanceSummary(BaseModel):
    """Schema for attendance summary statistics."""

    total_events: int = Field(..., description="Total number of events")
    present: int = Field(..., description="Number of on-time attendances")
    late: int = Field(..., description="Number of late attendances")
    absent: int = Field(..., description="Number of absences")
    leave: int = Field(..., description="Number of approved leaves")
    makeup: int = Field(..., description="Number of approved makeups")
    attendance_rate: float = Field(
        ...,
        description="Attendance rate (present + late + leave + makeup) / total"
    )
    punctuality_rate: float = Field(
        ...,
        description="Punctuality rate (present) / (present + late)"
    )