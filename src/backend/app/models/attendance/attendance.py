"""
Attendance model for tracking user check-ins.

Design Philosophy (Linus: "Good Taste"):
- Single status ENUM eliminates boolean flag combinations
- UNIQUE(user_id, event_id) prevents duplicate check-ins
- Soft delete for audit trail
- No direct link to LeaveRequest/MakeupRequest (decoupled design)
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import ForeignKey, Index, String, Text, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin
from app.models.enums import AttendanceStatus

if TYPE_CHECKING:
    from app.models.auth.user import User
    from app.models.calendar.event import Event


class Attendance(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """Attendance record linking users to events with status tracking.

    Relationships:
    - user: User who has this attendance record
    - event: Event this attendance is for

    Design Decisions (Linus Philosophy):
    1. ENUM status eliminates boolean flags:
       - No "is_present AND is_late" contradictions
       - Single field for all states
       - Extensible without schema changes

    2. UNIQUE(user_id, event_id):
       - Prevents duplicate check-ins
       - Database-level constraint (fail fast)

    3. No direct link to requests:
       - Attendance is FACT (what happened)
       - LeaveRequest is PROCESS (what's requested)
       - Decoupling simplifies state transitions

    4. Soft delete:
       - Audit trail for attendance records
       - Can restore mistaken deletions
    """

    __tablename__ = "attendance"
    __table_args__ = (
        Index(
            "idx_unique_user_event_active",
            "user_id", "event_id",
            unique=True,
            postgresql_where=text("deleted_at IS NULL")  # Only for non-deleted records
        ),
        {"comment": "Attendance records linking users to events with status tracking"}
    )

    # Foreign Keys
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User who has this attendance record"
    )

    event_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Event this attendance is for"
    )

    # Attendance Status (ENUM - eliminates boolean flags)
    status: Mapped[AttendanceStatus] = mapped_column(
        String(20),
        nullable=False,
        default=AttendanceStatus.ABSENT.value,
        server_default=AttendanceStatus.ABSENT.value,
        index=True,
        comment="Attendance status: PRESENT, LATE, ABSENT, LEAVE, MAKEUP, EARLY_LEAVE"
    )

    # Check-in Time (nullable for ABSENT/LEAVE)
    check_in_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Actual check-in timestamp (NULL for ABSENT/LEAVE)"
    )

    # Notes (for makeup/leave reasons)
    note: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Additional notes (reason for makeup/leave)"
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="attendances",
        foreign_keys=[user_id],
        lazy="select"
    )

    event: Mapped["Event"] = relationship(
        "Event",
        back_populates="attendances",
        foreign_keys=[event_id],
        lazy="select"
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<Attendance(id={self.id}, user_id={self.user_id}, event_id={self.event_id}, status={self.status})>"

    def mark_present(self, check_in_time: datetime) -> None:
        """Mark attendance as present with check-in time.

        Args:
            check_in_time: Time of check-in
        """
        self.status = AttendanceStatus.PRESENT
        self.check_in_time = check_in_time

    def mark_late(self, check_in_time: datetime) -> None:
        """Mark attendance as late with check-in time.

        Args:
            check_in_time: Time of late check-in
        """
        self.status = AttendanceStatus.LATE
        self.check_in_time = check_in_time

    def mark_leave(self, note: Optional[str] = None) -> None:
        """Mark attendance as approved leave.

        Args:
            note: Optional leave reason
        """
        self.status = AttendanceStatus.LEAVE
        self.check_in_time = None  # Leave has no check-in time
        if note:
            self.note = note

    def mark_makeup(self, note: str) -> None:
        """Mark attendance as approved makeup (補簽).

        Args:
            note: Reason for makeup request
        """
        self.status = AttendanceStatus.MAKEUP
        if note:
            self.note = note

    @property
    def is_present_or_late(self) -> bool:
        """Check if user checked in (present or late)."""
        return self.status in (AttendanceStatus.PRESENT, AttendanceStatus.LATE)

    @property
    def is_excused(self) -> bool:
        """Check if absence is excused (leave or makeup)."""
        return self.status in (AttendanceStatus.LEAVE, AttendanceStatus.MAKEUP)
