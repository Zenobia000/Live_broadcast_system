"""
Event model for Google Calendar synchronization.

Design Philosophy:
- Events are immutable historical facts (no soft delete)
- creator field nullable for system-synced events (avoids fake "system user")
- Grace period for late check-in logic
"""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.attendance.attendance import Attendance
    from app.models.attendance.leave_request import LeaveRequest
    from app.models.attendance.makeup_request import MakeupRequest
    from app.models.auth.user import User


class Event(Base, UUIDMixin, TimestampMixin):
    """Event model synced from Google Calendar.

    Relationships:
    - creator: User who created this event (nullable for system-synced events)
    - attendances: Attendance records for this event
    - leave_requests: Leave requests for this event
    - makeup_requests: Makeup requests for this event

    Design Decisions (Linus: "Simplicity"):
    - created_by nullable: System-synced events have no creator
      (avoids creating fake "system" user)
    - No soft delete: Events are historical facts
    - grace_period_minutes: Flexible late check-in policy per event
    """

    __tablename__ = "events"
    __table_args__ = (
        CheckConstraint(
            "end_time > start_time",
            name="check_event_time_range"
        ),
        CheckConstraint(
            "grace_period_minutes >= 0 AND grace_period_minutes <= 60",
            name="check_grace_period_range"
        ),
        {"comment": "Events synced from Google Calendar requiring attendance tracking"}
    )

    # Event Details
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Event title"
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Event description (optional)"
    )

    # Timing
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Event start time (UTC)"
    )

    end_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Event end time (UTC)"
    )

    grace_period_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=5,
        server_default="5",
        comment="Minutes after start_time before marking as LATE (default: 5)"
    )

    # Google Calendar Integration
    google_event_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Google Calendar Event ID (unique identifier from Google API)"
    )

    # Creator (nullable for system-synced events)
    created_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User who created this event (NULL for system-synced events)"
    )

    # Relationships
    creator: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="created_events",
        foreign_keys=[created_by],
        lazy="select"
    )

    attendances: Mapped[List["Attendance"]] = relationship(
        "Attendance",
        back_populates="event",
        foreign_keys="Attendance.event_id",
        lazy="select",
        cascade="all, delete-orphan"
    )

    leave_requests: Mapped[List["LeaveRequest"]] = relationship(
        "LeaveRequest",
        back_populates="event",
        foreign_keys="LeaveRequest.event_id",
        lazy="select",
        cascade="all, delete-orphan"
    )

    makeup_requests: Mapped[List["MakeupRequest"]] = relationship(
        "MakeupRequest",
        back_populates="event",
        foreign_keys="MakeupRequest.event_id",
        lazy="select",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<Event(id={self.id}, title={self.title}, start={self.start_time})>"

    @property
    def duration_minutes(self) -> int:
        """Calculate event duration in minutes."""
        return int((self.end_time - self.start_time).total_seconds() / 60)

    def is_late_checkin(self, checkin_time: datetime) -> bool:
        """Check if a check-in time is considered late.

        Args:
            checkin_time: The time when user checked in

        Returns:
            True if check-in is after grace period, False otherwise
        """
        from datetime import timedelta
        grace_deadline = self.start_time + timedelta(minutes=self.grace_period_minutes)
        return checkin_time > grace_deadline

    def is_ongoing(self, current_time: Optional[datetime] = None) -> bool:
        """Check if event is currently ongoing.

        Args:
            current_time: Time to check against (default: now)

        Returns:
            True if event is ongoing, False otherwise
        """
        if current_time is None:
            current_time = datetime.utcnow()
        return self.start_time <= current_time <= self.end_time
