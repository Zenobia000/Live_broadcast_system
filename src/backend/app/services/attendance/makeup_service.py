"""
Makeup request service for handling retroactive check-in applications.

Design Philosophy:
- Service layer for makeup request business logic
- State machine for approval workflow
- Integration with attendance updates for approved requests
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from app.models.attendance.makeup_request import MakeupRequest
from app.models.enums import RequestStatus
from app.repositories.attendance.attendance_repository import AttendanceRepository
from app.repositories.attendance.makeup_request_repository import MakeupRequestRepository


class MakeupService:
    """Service for makeup request management."""

    def __init__(
        self,
        makeup_request_repository: MakeupRequestRepository,
        attendance_repository: AttendanceRepository
    ):
        self.makeup_request_repository = makeup_request_repository
        self.attendance_repository = attendance_repository

    async def submit_makeup_request(
        self,
        user_id: UUID,
        event_id: UUID,
        reason: str
    ) -> MakeupRequest:
        """Submit a new makeup request.

        Args:
            user_id: User ID
            event_id: Event ID
            reason: Reason for makeup request

        Returns:
            Created makeup request

        Raises:
            ValueError: If makeup request already exists
        """
        # Check if makeup request already exists for this user and event
        existing_request = await self.makeup_request_repository.get_by_user_and_event(
            user_id, event_id
        )
        if existing_request:
            raise ValueError("Makeup request already exists for this event")

        return await self.makeup_request_repository.create(
            user_id=user_id,
            event_id=event_id,
            reason=reason
        )

    async def get_user_makeup_requests(
        self,
        user_id: UUID,
        status: Optional[RequestStatus] = None
    ) -> List[MakeupRequest]:
        """Get makeup requests for a user."""
        return await self.makeup_request_repository.list_by_user(
            user_id=user_id,
            status=status
        )

    async def get_pending_requests(
        self,
        limit: int = 50,
        offset: int = 0
    ) -> List[MakeupRequest]:
        """Get pending makeup requests for admin review."""
        return await self.makeup_request_repository.list_pending_requests(
            limit=limit,
            offset=offset
        )

    async def approve_makeup_request(
        self,
        request_id: UUID,
        reviewer_id: UUID,
        note: Optional[str] = None
    ) -> MakeupRequest:
        """Approve makeup request and update attendance.

        Args:
            request_id: Makeup request ID
            reviewer_id: Reviewer user ID
            note: Optional review note

        Returns:
            Approved makeup request

        Raises:
            ValueError: If request not found or cannot be approved
        """
        # Approve the makeup request
        makeup_request = await self.makeup_request_repository.approve_request(
            request_id=request_id,
            reviewer_id=reviewer_id,
            note=note
        )

        if not makeup_request:
            raise ValueError("Makeup request not found")

        # Update corresponding attendance record
        await self.attendance_repository.mark_as_makeup(
            user_id=makeup_request.user_id,
            event_id=makeup_request.event_id,
            note=f"Approved makeup: {makeup_request.reason}"
        )

        return makeup_request

    async def reject_makeup_request(
        self,
        request_id: UUID,
        reviewer_id: UUID,
        note: str
    ) -> MakeupRequest:
        """Reject makeup request.

        Args:
            request_id: Makeup request ID
            reviewer_id: Reviewer user ID
            note: Review note (required for rejection)

        Returns:
            Rejected makeup request

        Raises:
            ValueError: If request not found or cannot be rejected
        """
        makeup_request = await self.makeup_request_repository.reject_request(
            request_id=request_id,
            reviewer_id=reviewer_id,
            note=note
        )

        if not makeup_request:
            raise ValueError("Makeup request not found")

        return makeup_request

    async def get_makeup_request(self, request_id: UUID) -> Optional[MakeupRequest]:
        """Get makeup request by ID."""
        return await self.makeup_request_repository.get_by_id(request_id)

    async def cancel_makeup_request(
        self, request_id: UUID, user_id: UUID
    ) -> MakeupRequest:
        """Cancel pending makeup request (user can only cancel their own).

        Args:
            request_id: Makeup request ID
            user_id: User ID (for ownership verification)

        Returns:
            Cancelled makeup request

        Raises:
            ValueError: If request not found, not owned by user, or not pending
        """
        makeup_request = await self.makeup_request_repository.get_by_id(request_id)
        if not makeup_request:
            raise ValueError("Makeup request not found")

        if makeup_request.user_id != user_id:
            raise ValueError("Can only cancel your own makeup requests")

        if makeup_request.status != RequestStatus.PENDING:
            raise ValueError("Can only cancel pending makeup requests")

        # Soft delete the request (cancellation)
        await self.makeup_request_repository.soft_delete(makeup_request)
        return makeup_request