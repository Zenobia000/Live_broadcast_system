"""
Review service for leave and makeup request approval workflow.

Design Philosophy (Linus: "Good Taste"):
- Unified interface for both leave and makeup reviews
- State machine pattern eliminates special cases
- Atomic operations for request approval + attendance update
"""

from typing import List, Optional, Union
from uuid import UUID

from app.models.attendance.leave_request import LeaveRequest
from app.models.attendance.makeup_request import MakeupRequest
from app.models.enums import RequestStatus
from app.services.attendance.leave_service import LeaveService
from app.services.attendance.makeup_service import MakeupService


class ReviewService:
    """Service for unified leave and makeup request review."""

    def __init__(
        self,
        leave_service: LeaveService,
        makeup_service: MakeupService
    ):
        self.leave_service = leave_service
        self.makeup_service = makeup_service

    async def get_pending_reviews(
        self,
        limit: int = 50,
        offset: int = 0
    ) -> dict:
        """Get all pending requests for admin review.

        Args:
            limit: Maximum number of requests to return
            offset: Number of requests to skip

        Returns:
            Dictionary with leave and makeup requests
        """
        # Get pending requests from both services
        pending_leave_requests = await self.leave_service.get_pending_requests(
            limit=limit // 2,
            offset=offset // 2
        )
        pending_makeup_requests = await self.makeup_service.get_pending_requests(
            limit=limit // 2,
            offset=offset // 2
        )

        return {
            "leave_requests": pending_leave_requests,
            "makeup_requests": pending_makeup_requests,
            "total_leave": len(pending_leave_requests),
            "total_makeup": len(pending_makeup_requests),
            "total_pending": len(pending_leave_requests) + len(pending_makeup_requests)
        }

    async def approve_request(
        self,
        request_type: str,
        request_id: UUID,
        reviewer_id: UUID,
        note: Optional[str] = None
    ) -> Union[LeaveRequest, MakeupRequest]:
        """Approve leave or makeup request.

        Args:
            request_type: "leave" or "makeup"
            request_id: Request ID
            reviewer_id: Reviewer user ID
            note: Optional review note

        Returns:
            Approved request object

        Raises:
            ValueError: If request type invalid or approval fails
        """
        if request_type == "leave":
            return await self.leave_service.approve_leave_request(
                request_id=request_id,
                reviewer_id=reviewer_id,
                note=note
            )
        elif request_type == "makeup":
            return await self.makeup_service.approve_makeup_request(
                request_id=request_id,
                reviewer_id=reviewer_id,
                note=note
            )
        else:
            raise ValueError("Request type must be 'leave' or 'makeup'")

    async def reject_request(
        self,
        request_type: str,
        request_id: UUID,
        reviewer_id: UUID,
        note: str
    ) -> Union[LeaveRequest, MakeupRequest]:
        """Reject leave or makeup request.

        Args:
            request_type: "leave" or "makeup"
            request_id: Request ID
            reviewer_id: Reviewer user ID
            note: Review note (required for rejection)

        Returns:
            Rejected request object

        Raises:
            ValueError: If request type invalid or rejection fails
        """
        if not note.strip():
            raise ValueError("Review note is required for rejection")

        if request_type == "leave":
            return await self.leave_service.reject_leave_request(
                request_id=request_id,
                reviewer_id=reviewer_id,
                note=note
            )
        elif request_type == "makeup":
            return await self.makeup_service.reject_makeup_request(
                request_id=request_id,
                reviewer_id=reviewer_id,
                note=note
            )
        else:
            raise ValueError("Request type must be 'leave' or 'makeup'")

    async def get_request_details(
        self, request_type: str, request_id: UUID
    ) -> Optional[Union[LeaveRequest, MakeupRequest]]:
        """Get request details by type and ID.

        Args:
            request_type: "leave" or "makeup"
            request_id: Request ID

        Returns:
            Request object or None if not found

        Raises:
            ValueError: If request type invalid
        """
        if request_type == "leave":
            return await self.leave_service.get_leave_request(request_id)
        elif request_type == "makeup":
            return await self.makeup_service.get_makeup_request(request_id)
        else:
            raise ValueError("Request type must be 'leave' or 'makeup'")

    async def get_user_requests(
        self,
        user_id: UUID,
        status: Optional[RequestStatus] = None
    ) -> dict:
        """Get all requests submitted by a user.

        Args:
            user_id: User ID
            status: Filter by status (optional)

        Returns:
            Dictionary with user's leave and makeup requests
        """
        leave_requests = await self.leave_service.get_user_leave_requests(
            user_id=user_id,
            status=status
        )
        makeup_requests = await self.makeup_service.get_user_makeup_requests(
            user_id=user_id,
            status=status
        )

        return {
            "leave_requests": leave_requests,
            "makeup_requests": makeup_requests,
            "total_leave": len(leave_requests),
            "total_makeup": len(makeup_requests),
            "total_requests": len(leave_requests) + len(makeup_requests)
        }