"""Leave request model for absence approval workflow."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin
from app.models.enums import LeaveType, RequestStatus

if TYPE_CHECKING:
    from app.models.auth.user import User
    from app.models.calendar.event import Event


class LeaveRequest(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """Leave application with approval workflow."""

    __tablename__ = "leave_requests"
    __table_args__ = (
        CheckConstraint("end_time >= start_time", name="check_leave_time_range"),
        CheckConstraint(
            "(status = 'PENDING' AND reviewed_by IS NULL AND reviewed_at IS NULL) OR "
            "(status IN ('APPROVED', 'REJECTED') AND reviewed_by IS NOT NULL AND reviewed_at IS NOT NULL)",
            name="check_leave_review_consistency"
        ),
        {"comment": "Leave applications with approval workflow"}
    )

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    event_id: Mapped[int] = mapped_column(Integer, ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    leave_type: Mapped[LeaveType] = mapped_column(
        String(20),
        nullable=False,
        comment="Type: SICK, PERSONAL, OFFICIAL, OTHER"
    )

    reason: Mapped[str] = mapped_column(Text, nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    status: Mapped[RequestStatus] = mapped_column(
        String(20),
        nullable=False,
        default=RequestStatus.PENDING.value,
        server_default=RequestStatus.PENDING.value,
        index=True
    )

    reviewed_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    review_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="submitted_leave_requests",
        foreign_keys=[user_id]
    )

    event: Mapped["Event"] = relationship(
        "Event",
        back_populates="leave_requests",
        foreign_keys=[event_id]
    )

    reviewer: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="reviewed_leave_requests",
        foreign_keys=[reviewed_by]
    )

    def approve(self, reviewer_id: int, note: Optional[str] = None) -> None:
        """Approve leave request."""
        self.status = RequestStatus.APPROVED
        self.reviewed_by = reviewer_id
        self.review_note = note
        self.reviewed_at = datetime.utcnow()

    def reject(self, reviewer_id: int, note: str) -> None:
        """Reject leave request with reason."""
        self.status = RequestStatus.REJECTED
        self.reviewed_by = reviewer_id
        self.review_note = note
        self.reviewed_at = datetime.utcnow()
