"""
Leave request service for handling leave applications and approvals.

Design Philosophy:
- Service layer for leave request business logic
- State machine for approval workflow
- Integration with attendance updates
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from app.models.attendance.leave_request import LeaveRequest
from app.models.enums import LeaveType, RequestStatus
from app.repositories.attendance.attendance_repository import AttendanceRepository
from app.repositories.attendance.leave_request_repository import LeaveRequestRepository


class LeaveService:
    """Service for leave request management."""

    def __init__(
        self,
        leave_request_repository: LeaveRequestRepository,
        attendance_repository: AttendanceRepository
    ):
        self.leave_request_repository = leave_request_repository
        self.attendance_repository = attendance_repository

    async def submit_leave_request(
        self,
        user_id: UUID,
        event_id: UUID,
        leave_type: LeaveType,
        reason: str,
        start_time: datetime,
        end_time: datetime
    ) -> LeaveRequest:
        """Submit a new leave request.

        Args:
            user_id: User ID
            event_id: Event ID
            leave_type: Type of leave
            reason: Reason for leave
            start_time: Leave start time
            end_time: Leave end time

        Returns:
            Created leave request

        Raises:
            ValueError: If leave request already exists or invalid times
        """
        # Validate time range
        if end_time <= start_time:
            raise ValueError("End time must be after start time")

        # Check if leave request already exists for this user and event
        existing_request = await self.leave_request_repository.get_by_user_and_event(
            user_id, event_id
        )
        if existing_request:
            raise ValueError("Leave request already exists for this event")

        return await self.leave_request_repository.create(
            user_id=user_id,
            event_id=event_id,
            leave_type=leave_type,
            reason=reason,
            start_time=start_time,
            end_time=end_time
        )

    async def get_user_leave_requests(
        self,
        user_id: UUID,
        status: Optional[RequestStatus] = None
    ) -> List[LeaveRequest]:
        """Get leave requests for a user."""
        return await self.leave_request_repository.list_by_user(
            user_id=user_id,
            status=status
        )

    async def get_pending_requests(
        self,
        limit: int = 50,
        offset: int = 0
    ) -> List[LeaveRequest]:
        """Get pending leave requests for admin review."""
        return await self.leave_request_repository.list_pending_requests(
            limit=limit,
            offset=offset
        )

    async def approve_leave_request(
        self,
        request_id: UUID,
        reviewer_id: UUID,
        note: Optional[str] = None
    ) -> LeaveRequest:
        """Approve leave request and update attendance.

        Args:
            request_id: Leave request ID
            reviewer_id: Reviewer user ID
            note: Optional review note

        Returns:
            Approved leave request

        Raises:
            ValueError: If request not found or cannot be approved
        """
        # Approve the leave request
        leave_request = await self.leave_request_repository.approve_request(
            request_id=request_id,
            reviewer_id=reviewer_id,
            note=note
        )

        if not leave_request:
            raise ValueError("Leave request not found")

        # Update corresponding attendance record
        await self.attendance_repository.mark_as_leave(
            user_id=leave_request.user_id,
            event_id=leave_request.event_id,
            note=f"Approved leave: {leave_request.reason}"
        )

        return leave_request

    async def reject_leave_request(
        self,
        request_id: UUID,
        reviewer_id: UUID,
        note: str
    ) -> LeaveRequest:
        """Reject leave request.

        Args:
            request_id: Leave request ID
            reviewer_id: Reviewer user ID
            note: Review note (required for rejection)

        Returns:
            Rejected leave request

        Raises:
            ValueError: If request not found or cannot be rejected
        """
        leave_request = await self.leave_request_repository.reject_request(
            request_id=request_id,
            reviewer_id=reviewer_id,
            note=note
        )

        if not leave_request:
            raise ValueError("Leave request not found")

        return leave_request

    async def get_leave_request(self, request_id: UUID) -> Optional[LeaveRequest]:
        """Get leave request by ID."""
        return await self.leave_request_repository.get_by_id(request_id)

    async def cancel_leave_request(
        self, request_id: UUID, user_id: UUID
    ) -> LeaveRequest:
        """Cancel pending leave request (user can only cancel their own).

        Args:
            request_id: Leave request ID
            user_id: User ID (for ownership verification)

        Returns:
            Cancelled leave request

        Raises:
            ValueError: If request not found, not owned by user, or not pending
        """
        leave_request = await self.leave_request_repository.get_by_id(request_id)
        if not leave_request:
            raise ValueError("Leave request not found")

        if leave_request.user_id != user_id:
            raise ValueError("Can only cancel your own leave requests")

        if leave_request.status != RequestStatus.PENDING:
            raise ValueError("Can only cancel pending leave requests")

        # Soft delete the request (cancellation)
        await self.leave_request_repository.soft_delete(leave_request)
        return leave_request