"""
Leave and Makeup request Pydantic schemas for API input/output validation.

Design Philosophy:
- Unified schemas for both request types
- Clear approval workflow support
- Comprehensive request information
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import LeaveType, RequestStatus


# Leave Request Schemas
class LeaveRequestBase(BaseModel):
    """Base leave request schema."""

    event_id: UUID = Field(..., description="Event ID for leave request")
    leave_type: LeaveType = Field(..., description="Type of leave")
    reason: str = Field(..., min_length=5, max_length=1000, description="Reason for leave")
    start_time: datetime = Field(..., description="Leave start time")
    end_time: datetime = Field(..., description="Leave end time")


class LeaveRequestCreate(LeaveRequestBase):
    """Schema for creating leave request."""
    pass


class LeaveRequestUpdate(BaseModel):
    """Schema for updating leave request (before approval)."""

    leave_type: Optional[LeaveType] = Field(None, description="Type of leave")
    reason: Optional[str] = Field(None, min_length=5, max_length=1000, description="Reason for leave")
    start_time: Optional[datetime] = Field(None, description="Leave start time")
    end_time: Optional[datetime] = Field(None, description="Leave end time")


class LeaveRequestResponse(LeaveRequestBase):
    """Schema for leave request API responses."""

    id: UUID = Field(..., description="Leave request ID")
    user_id: UUID = Field(..., description="User ID")
    status: RequestStatus = Field(..., description="Request status")
    reviewed_by: Optional[UUID] = Field(None, description="Reviewer user ID")
    review_note: Optional[str] = Field(None, description="Review note")
    reviewed_at: Optional[datetime] = Field(None, description="Review timestamp")
    created_at: datetime = Field(..., description="Request creation time")
    updated_at: datetime = Field(..., description="Request last update time")

    class Config:
        from_attributes = True


# Makeup Request Schemas
class MakeupRequestBase(BaseModel):
    """Base makeup request schema."""

    event_id: UUID = Field(..., description="Event ID for makeup request")
    reason: str = Field(..., min_length=5, max_length=1000, description="Reason for makeup")


class MakeupRequestCreate(MakeupRequestBase):
    """Schema for creating makeup request."""
    pass


class MakeupRequestUpdate(BaseModel):
    """Schema for updating makeup request (before approval)."""

    reason: Optional[str] = Field(None, min_length=5, max_length=1000, description="Reason for makeup")


class MakeupRequestResponse(MakeupRequestBase):
    """Schema for makeup request API responses."""

    id: UUID = Field(..., description="Makeup request ID")
    user_id: UUID = Field(..., description="User ID")
    status: RequestStatus = Field(..., description="Request status")
    reviewed_by: Optional[UUID] = Field(None, description="Reviewer user ID")
    review_note: Optional[str] = Field(None, description="Review note")
    reviewed_at: Optional[datetime] = Field(None, description="Review timestamp")
    created_at: datetime = Field(..., description="Request creation time")
    updated_at: datetime = Field(..., description="Request last update time")

    class Config:
        from_attributes = True


# Review Schemas
class ReviewRequest(BaseModel):
    """Schema for reviewing requests."""

    action: str = Field(..., pattern="^(approve|reject)$", description="Review action: approve or reject")
    note: Optional[str] = Field(None, max_length=1000, description="Review note (required for rejection)")


class ReviewResponse(BaseModel):
    """Schema for review action response."""

    request_id: UUID = Field(..., description="Request ID")
    request_type: str = Field(..., description="Request type: leave or makeup")
    action: str = Field(..., description="Review action taken")
    reviewer_id: UUID = Field(..., description="Reviewer user ID")
    message: str = Field(..., description="Review result message")


class PendingReviewsResponse(BaseModel):
    """Schema for pending reviews response."""

    leave_requests: List[LeaveRequestResponse] = Field(..., description="Pending leave requests")
    makeup_requests: List[MakeupRequestResponse] = Field(..., description="Pending makeup requests")
    total_leave: int = Field(..., description="Total pending leave requests")
    total_makeup: int = Field(..., description="Total pending makeup requests")
    total_pending: int = Field(..., description="Total pending requests")


class UserRequestsResponse(BaseModel):
    """Schema for user's requests response."""

    leave_requests: List[LeaveRequestResponse] = Field(..., description="User's leave requests")
    makeup_requests: List[MakeupRequestResponse] = Field(..., description="User's makeup requests")
    total_leave: int = Field(..., description="Total leave requests")
    total_makeup: int = Field(..., description="Total makeup requests")
    total_requests: int = Field(..., description="Total requests")