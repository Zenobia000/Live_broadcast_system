"""
Base models and mixins for SQLAlchemy ORM.

This module provides:
- Base declarative class for all models
- Common mixins for timestamps and soft delete
- UUID primary key mixin

Design Philosophy (Linus Torvalds):
- "Good programmers worry about data structures and their relationships"
- Common patterns extracted to avoid repetition
- Type hints for clarity and IDE support
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


class UUIDMixin:
    """Mixin for UUID primary key.

    Uses PostgreSQL's uuid_generate_v4() for server-side generation.
    """

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=func.uuid_generate_v4(),
        comment="Primary key (UUID)"
    )


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps.

    Timestamps are stored in UTC with timezone awareness.
    updated_at is automatically updated on record modification via trigger.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Record creation timestamp (UTC)"
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Record last update timestamp (UTC)"
    )


class SoftDeleteMixin:
    """Mixin for soft delete functionality.

    Soft delete allows "deleting" records by marking them with deleted_at timestamp
    while preserving data for audit trails. Only used for core business tables:
    - Attendance
    - LeaveRequest
    - MakeupRequest

    Design Decision (Linus: "Simplicity"):
    - User and Event tables don't use soft delete (they're immutable historical facts)
    - Soft delete only where audit trail is critical
    """

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        comment="Soft delete timestamp (NULL = active record)"
    )

    @property
    def is_deleted(self) -> bool:
        """Check if record is soft-deleted."""
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        """Mark record as deleted."""
        self.deleted_at = datetime.utcnow()

    def restore(self) -> None:
        """Restore soft-deleted record."""
        self.deleted_at = None
