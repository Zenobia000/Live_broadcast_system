"""
Makeup request repository for database operations.

Design Philosophy:
- Repository pattern for makeup request data access
- Support for approval workflow operations
- Consistent interface with leave request operations
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attendance.makeup_request import MakeupRequest
from app.models.enums import RequestStatus


class MakeupRequestRepository:
    """Repository for MakeupRequest model database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        user_id: UUID,
        event_id: UUID,
        reason: str
    ) -> MakeupRequest:
        """Create a new makeup request."""
        makeup_request = MakeupRequest(
            user_id=user_id,
            event_id=event_id,
            reason=reason,
            status=RequestStatus.PENDING
        )
        self.session.add(makeup_request)
        await self.session.commit()
        await self.session.refresh(makeup_request)
        return makeup_request

    async def get_by_id(self, request_id: UUID) -> Optional[MakeupRequest]:
        """Get makeup request by ID."""
        result = await self.session.execute(
            select(MakeupRequest).where(
                and_(
                    MakeupRequest.id == request_id,
                    MakeupRequest.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_by_user(
        self,
        user_id: UUID,
        status: Optional[RequestStatus] = None,
        limit: int = 50
    ) -> List[MakeupRequest]:
        """List makeup requests by user."""
        query = select(MakeupRequest).where(
            and_(
                MakeupRequest.user_id == user_id,
                MakeupRequest.deleted_at.is_(None)
            )
        )

        if status:
            query = query.where(MakeupRequest.status == status)

        query = query.order_by(MakeupRequest.created_at.desc()).limit(limit)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def list_by_event(self, event_id: UUID) -> List[MakeupRequest]:
        """List makeup requests for specific event."""
        result = await self.session.execute(
            select(MakeupRequest).where(
                and_(
                    MakeupRequest.event_id == event_id,
                    MakeupRequest.deleted_at.is_(None)
                )
            ).order_by(MakeupRequest.created_at)
        )
        return result.scalars().all()

    async def list_pending_requests(
        self,
        limit: int = 50,
        offset: int = 0
    ) -> List[MakeupRequest]:
        """List pending makeup requests for admin review."""
        result = await self.session.execute(
            select(MakeupRequest).where(
                and_(
                    MakeupRequest.status == RequestStatus.PENDING,
                    MakeupRequest.deleted_at.is_(None)
                )
            )
            .order_by(MakeupRequest.created_at)
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_user_and_event(
        self, user_id: UUID, event_id: UUID
    ) -> Optional[MakeupRequest]:
        """Get makeup request for specific user and event."""
        result = await self.session.execute(
            select(MakeupRequest).where(
                and_(
                    MakeupRequest.user_id == user_id,
                    MakeupRequest.event_id == event_id,
                    MakeupRequest.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    async def update(self, makeup_request: MakeupRequest) -> MakeupRequest:
        """Update makeup request."""
        await self.session.commit()
        await self.session.refresh(makeup_request)
        return makeup_request

    async def soft_delete(self, makeup_request: MakeupRequest) -> None:
        """Soft delete makeup request."""
        makeup_request.soft_delete()
        await self.session.commit()

    async def approve_request(
        self,
        request_id: UUID,
        reviewer_id: UUID,
        note: Optional[str] = None
    ) -> Optional[MakeupRequest]:
        """Approve makeup request.

        Args:
            request_id: Makeup request ID
            reviewer_id: Reviewer user ID
            note: Optional review note

        Returns:
            Updated makeup request or None if not found

        Raises:
            ValueError: If request is not in PENDING status
        """
        makeup_request = await self.get_by_id(request_id)
        if not makeup_request:
            return None

        if makeup_request.status != RequestStatus.PENDING:
            raise ValueError(f"Cannot approve request with status: {makeup_request.status}")

        makeup_request.approve(reviewer_id, note)
        return await self.update(makeup_request)

    async def reject_request(
        self,
        request_id: UUID,
        reviewer_id: UUID,
        note: str
    ) -> Optional[MakeupRequest]:
        """Reject makeup request.

        Args:
            request_id: Makeup request ID
            reviewer_id: Reviewer user ID
            note: Review note (required for rejection)

        Returns:
            Updated makeup request or None if not found

        Raises:
            ValueError: If request is not in PENDING status
        """
        makeup_request = await self.get_by_id(request_id)
        if not makeup_request:
            return None

        if makeup_request.status != RequestStatus.PENDING:
            raise ValueError(f"Cannot reject request with status: {makeup_request.status}")

        makeup_request.reject(reviewer_id, note)
        return await self.update(makeup_request)

    async def exists_by_user_and_event(
        self, user_id: UUID, event_id: UUID
    ) -> bool:
        """Check if makeup request exists for user and event."""
        result = await self.session.execute(
            select(MakeupRequest.id).where(
                and_(
                    MakeupRequest.user_id == user_id,
                    MakeupRequest.event_id == event_id,
                    MakeupRequest.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none() is not None