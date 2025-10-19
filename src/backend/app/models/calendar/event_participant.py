"""
EventParticipant model for managing event invitations and participants.

Design Philosophy:
- Many-to-many relationship between Events and Users
- Tracks invitation and notification status
- Enables targeted notifications for specific participants
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, UniqueConstraint

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.calendar.event import Event
    from app.models.auth.user import User


class EventParticipant(Base, UUIDMixin, TimestampMixin):
    """EventParticipant model for event invitations.

    Relationships:
    - event: The event this participation is for
    - user: The user invited to the event

    Design Decisions (Linus: "Good Taste"):
    - UNIQUE(event_id, user_id): Prevents duplicate invitations
    - notification_sent: Tracks whether invitation email/slack was sent
    - No soft delete: Removing a participant is a hard delete operation
    """

    __tablename__ = "event_participants"
    __table_args__ = (
        UniqueConstraint(
            "event_id",
            "user_id",
            name="uq_event_participant"
        ),
        {"comment": "Event participants and invitation tracking"}
    )

    # Foreign Keys
    event_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Event ID (CASCADE delete when event is deleted)"
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User ID (CASCADE delete when user is deleted)"
    )

    # Invitation Status
    invited_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        comment="When the invitation was sent"
    )

    notification_sent: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
        comment="Whether notification (Email/Slack) was sent"
    )

    # Relationships
    event: Mapped["Event"] = relationship(
        "Event",
        back_populates="participants",
        lazy="select"
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="event_participations",
        lazy="select"
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<EventParticipant(event_id={self.event_id}, user_id={self.user_id})>"

    def mark_notification_sent(self) -> None:
        """Mark notification as sent."""
        self.notification_sent = True
