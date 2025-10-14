"""
Leave request repository for database operations.

Design Philosophy:
- Repository pattern for leave request data access
- Support for approval workflow operations
- Efficient filtering and querying
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attendance.leave_request import LeaveRequest
from app.models.enums import LeaveType, RequestStatus


class LeaveRequestRepository:
    """Repository for LeaveRequest model database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        user_id: UUID,
        event_id: UUID,
        leave_type: LeaveType,
        reason: str,
        start_time: datetime,
        end_time: datetime
    ) -> LeaveRequest:
        """Create a new leave request."""
        leave_request = LeaveRequest(
            user_id=user_id,
            event_id=event_id,
            leave_type=leave_type,
            reason=reason,
            start_time=start_time,
            end_time=end_time,
            status=RequestStatus.PENDING
        )
        self.session.add(leave_request)
        await self.session.commit()
        await self.session.refresh(leave_request)
        return leave_request

    async def get_by_id(self, request_id: UUID) -> Optional[LeaveRequest]:
        """Get leave request by ID."""
        result = await self.session.execute(
            select(LeaveRequest).where(
                and_(
                    LeaveRequest.id == request_id,
                    LeaveRequest.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_by_user(
        self,
        user_id: UUID,
        status: Optional[RequestStatus] = None,
        limit: int = 50
    ) -> List[LeaveRequest]:
        """List leave requests by user."""
        query = select(LeaveRequest).where(
            and_(
                LeaveRequest.user_id == user_id,
                LeaveRequest.deleted_at.is_(None)
            )
        )

        if status:
            query = query.where(LeaveRequest.status == status)

        query = query.order_by(LeaveRequest.created_at.desc()).limit(limit)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def list_by_event(self, event_id: UUID) -> List[LeaveRequest]:
        """List leave requests for specific event."""
        result = await self.session.execute(
            select(LeaveRequest).where(
                and_(
                    LeaveRequest.event_id == event_id,
                    LeaveRequest.deleted_at.is_(None)
                )
            ).order_by(LeaveRequest.created_at)
        )
        return result.scalars().all()

    async def list_pending_requests(
        self,
        limit: int = 50,
        offset: int = 0
    ) -> List[LeaveRequest]:
        """List pending leave requests for admin review."""
        result = await self.session.execute(
            select(LeaveRequest).where(
                and_(
                    LeaveRequest.status == RequestStatus.PENDING,
                    LeaveRequest.deleted_at.is_(None)
                )
            )
            .order_by(LeaveRequest.created_at)
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_user_and_event(
        self, user_id: UUID, event_id: UUID
    ) -> Optional[LeaveRequest]:
        """Get leave request for specific user and event."""
        result = await self.session.execute(
            select(LeaveRequest).where(
                and_(
                    LeaveRequest.user_id == user_id,
                    LeaveRequest.event_id == event_id,
                    LeaveRequest.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    async def update(self, leave_request: LeaveRequest) -> LeaveRequest:
        """Update leave request."""
        await self.session.commit()
        await self.session.refresh(leave_request)
        return leave_request

    async def soft_delete(self, leave_request: LeaveRequest) -> None:
        """Soft delete leave request."""
        leave_request.soft_delete()
        await self.session.commit()

    async def approve_request(
        self,
        request_id: UUID,
        reviewer_id: UUID,
        note: Optional[str] = None
    ) -> Optional[LeaveRequest]:
        """Approve leave request.

        Args:
            request_id: Leave request ID
            reviewer_id: Reviewer user ID
            note: Optional review note

        Returns:
            Updated leave request or None if not found

        Raises:
            ValueError: If request is not in PENDING status
        """
        leave_request = await self.get_by_id(request_id)
        if not leave_request:
            return None

        if leave_request.status != RequestStatus.PENDING:
            raise ValueError(f"Cannot approve request with status: {leave_request.status}")

        leave_request.approve(reviewer_id, note)
        return await self.update(leave_request)

    async def reject_request(
        self,
        request_id: UUID,
        reviewer_id: UUID,
        note: str
    ) -> Optional[LeaveRequest]:
        """Reject leave request.

        Args:
            request_id: Leave request ID
            reviewer_id: Reviewer user ID
            note: Review note (required for rejection)

        Returns:
            Updated leave request or None if not found

        Raises:
            ValueError: If request is not in PENDING status
        """
        leave_request = await self.get_by_id(request_id)
        if not leave_request:
            return None

        if leave_request.status != RequestStatus.PENDING:
            raise ValueError(f"Cannot reject request with status: {leave_request.status}")

        leave_request.reject(reviewer_id, note)
        return await self.update(leave_request)

    async def exists_by_user_and_event(
        self, user_id: UUID, event_id: UUID
    ) -> bool:
        """Check if leave request exists for user and event."""
        result = await self.session.execute(
            select(LeaveRequest.id).where(
                and_(
                    LeaveRequest.user_id == user_id,
                    LeaveRequest.event_id == event_id,
                    LeaveRequest.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none() is not None