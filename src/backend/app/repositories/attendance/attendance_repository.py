"""
Attendance repository for database operations.

Design Philosophy:
- Repository pattern for data access
- Support for attendance status transitions
- Efficient queries for attendance reporting
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attendance.attendance import Attendance
from app.models.enums import AttendanceStatus


class AttendanceRepository:
    """Repository for Attendance model database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        user_id: int,
        event_id: int,
        status: AttendanceStatus = AttendanceStatus.ABSENT,
        check_in_time: Optional[datetime] = None,
        note: Optional[str] = None
    ) -> Attendance:
        """Create a new attendance record."""
        attendance = Attendance(
            user_id=user_id,
            event_id=event_id,
            status=status,
            check_in_time=check_in_time,
            note=note
        )
        self.session.add(attendance)
        await self.session.commit()
        await self.session.refresh(attendance)
        return attendance

    async def get_by_id(self, attendance_id: UUID) -> Optional[Attendance]:
        """Get attendance record by ID."""
        result = await self.session.execute(
            select(Attendance).where(
                and_(
                    Attendance.id == attendance_id,
                    Attendance.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_user_and_event(
        self, user_id: int, event_id: int
    ) -> Optional[Attendance]:
        """Get attendance record for specific user and event."""
        result = await self.session.execute(
            select(Attendance).where(
                and_(
                    Attendance.user_id == user_id,
                    Attendance.event_id == event_id,
                    Attendance.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_by_user(
        self,
        user_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Attendance]:
        """List attendance records for a user."""
        query = select(Attendance).where(
            and_(
                Attendance.user_id == user_id,
                Attendance.deleted_at.is_(None)
            )
        )

        # Note: Date filtering would require joining with Event table
        # For now, return all attendance records for the user
        # TODO: Implement proper date filtering with Event join

        query = query.order_by(Attendance.created_at.desc())

        result = await self.session.execute(query)
        return result.scalars().all()

    async def list_by_event(self, event_id: UUID) -> List[Attendance]:
        """List all attendance records for an event."""
        result = await self.session.execute(
            select(Attendance).where(
                and_(
                    Attendance.event_id == event_id,
                    Attendance.deleted_at.is_(None)
                )
            ).order_by(Attendance.check_in_time)
        )
        return result.scalars().all()

    async def update(self, attendance: Attendance) -> Attendance:
        """Update attendance record."""
        await self.session.commit()
        await self.session.refresh(attendance)
        return attendance

    async def soft_delete(self, attendance: Attendance) -> None:
        """Soft delete attendance record."""
        attendance.soft_delete()
        await self.session.commit()

    async def check_in_user(
        self,
        user_id: int,
        event_id: int,
        check_in_time: datetime,
        is_late: bool = False
    ) -> Attendance:
        """Check in user for an event.

        Args:
            user_id: User ID (integer)
            event_id: Event ID (integer)
            check_in_time: Time of check-in
            is_late: Whether check-in is late

        Returns:
            Updated attendance record

        Raises:
            ValueError: If attendance record doesn't exist
        """
        attendance = await self.get_by_user_and_event(user_id, event_id)
        if not attendance:
            # Create new attendance record if it doesn't exist
            attendance = await self.create(
                user_id=user_id,
                event_id=event_id,
                status=AttendanceStatus.LATE if is_late else AttendanceStatus.PRESENT,
                check_in_time=check_in_time
            )
        else:
            # Update existing record
            if is_late:
                attendance.mark_late(check_in_time)
            else:
                attendance.mark_present(check_in_time)
            attendance = await self.update(attendance)

        return attendance

    async def mark_as_leave(
        self,
        user_id: int,
        event_id: int,
        note: Optional[str] = None
    ) -> Attendance:
        """Mark attendance as approved leave.

        Args:
            user_id: User ID (integer)
            event_id: Event ID (integer)
            note: Leave reason

        Returns:
            Updated attendance record
        """
        attendance = await self.get_by_user_and_event(user_id, event_id)
        if not attendance:
            attendance = await self.create(
                user_id=user_id,
                event_id=event_id,
                status=AttendanceStatus.LEAVE,
                note=note
            )
        else:
            attendance.mark_leave(note)
            attendance = await self.update(attendance)

        return attendance

    async def mark_as_makeup(
        self,
        user_id: int,
        event_id: int,
        note: str
    ) -> Attendance:
        """Mark attendance as approved makeup.

        Args:
            user_id: User ID (integer)
            event_id: Event ID (integer)
            note: Makeup reason

        Returns:
            Updated attendance record
        """
        attendance = await self.get_by_user_and_event(user_id, event_id)
        if not attendance:
            attendance = await self.create(
                user_id=user_id,
                event_id=event_id,
                status=AttendanceStatus.MAKEUP,
                note=note
            )
        else:
            attendance.mark_makeup(note)
            attendance = await self.update(attendance)

        return attendance

    async def exists_by_user_and_event(
        self, user_id: UUID, event_id: UUID
    ) -> bool:
        """Check if attendance record exists for user and event."""
        result = await self.session.execute(
            select(Attendance.id).where(
                and_(
                    Attendance.user_id == user_id,
                    Attendance.event_id == event_id,
                    Attendance.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none() is not None