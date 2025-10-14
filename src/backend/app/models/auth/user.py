"""
User model for authentication and authorization.

Design Philosophy:
- 100% Google OAuth 2.0 authentication (no password storage)
- Role-based access control (RBAC) with UserRole enum
- Immutable user records (no soft delete - users are historical facts)
"""

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import UserRole

if TYPE_CHECKING:
    from app.models.attendance.attendance import Attendance
    from app.models.attendance.leave_request import LeaveRequest
    from app.models.attendance.makeup_request import MakeupRequest
    from app.models.calendar.event import Event


class User(Base, UUIDMixin, TimestampMixin):
    """User model for authentication via Google OAuth 2.0.

    Relationships:
    - created_events: Events created by this user (nullable - system events have no creator)
    - attendances: Attendance records for this user
    - submitted_leave_requests: Leave requests submitted by this user
    - reviewed_leave_requests: Leave requests reviewed by this user (admin only)
    - submitted_makeup_requests: Makeup requests submitted by this user
    - reviewed_makeup_requests: Makeup requests reviewed by this user (admin only)

    Design Decisions:
    - No password field (100% OAuth)
    - Email and google_id both unique (support account linking)
    - Role as ENUM (extensible to MODERATOR, etc.)
    - No soft delete (users are immutable historical facts)
    """

    __tablename__ = "users"
    __table_args__ = {"comment": "User accounts authenticated via Google OAuth 2.0"}

    # Authentication Fields (Google OAuth 2.0)
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Google OAuth email address (unique identifier)"
    )

    google_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Google OAuth user ID (sub claim from JWT)"
    )

    # Profile Fields
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="User display name"
    )

    avatar_url: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
        comment="User avatar URL (from Google profile)"
    )

    # Authorization
    role: Mapped[UserRole] = mapped_column(
        String(20),
        nullable=False,
        default=UserRole.MEMBER.value,
        server_default=UserRole.MEMBER.value,
        comment="User role: MEMBER (regular user) or ADMIN (administrator)"
    )

    # Relationships
    # Events created by this user (nullable - system-synced events have no creator)
    created_events: Mapped[List["Event"]] = relationship(
        "Event",
        back_populates="creator",
        foreign_keys="Event.created_by",
        lazy="select",
        cascade="all, delete-orphan"
    )

    # Attendance records
    attendances: Mapped[List["Attendance"]] = relationship(
        "Attendance",
        back_populates="user",
        foreign_keys="Attendance.user_id",
        lazy="select",
        cascade="all, delete-orphan"
    )

    # Leave requests submitted by this user
    submitted_leave_requests: Mapped[List["LeaveRequest"]] = relationship(
        "LeaveRequest",
        back_populates="user",
        foreign_keys="LeaveRequest.user_id",
        lazy="select",
        cascade="all, delete-orphan"
    )

    # Leave requests reviewed by this user (admin only)
    reviewed_leave_requests: Mapped[List["LeaveRequest"]] = relationship(
        "LeaveRequest",
        back_populates="reviewer",
        foreign_keys="LeaveRequest.reviewed_by",
        lazy="select"
    )

    # Makeup requests submitted by this user
    submitted_makeup_requests: Mapped[List["MakeupRequest"]] = relationship(
        "MakeupRequest",
        back_populates="user",
        foreign_keys="MakeupRequest.user_id",
        lazy="select",
        cascade="all, delete-orphan"
    )

    # Makeup requests reviewed by this user (admin only)
    reviewed_makeup_requests: Mapped[List["MakeupRequest"]] = relationship(
        "MakeupRequest",
        back_populates="reviewer",
        foreign_keys="MakeupRequest.reviewed_by",
        lazy="select"
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"

    @property
    def is_admin(self) -> bool:
        """Check if user has admin privileges."""
        return self.role == UserRole.ADMIN

    @property
    def is_member(self) -> bool:
        """Check if user is a regular member."""
        return self.role == UserRole.MEMBER
