"""
Database configuration and session management.

Design Philosophy (Linus's "Good Taste"):
- Single database session factory
- Proper connection lifecycle management
- Clean session dependency injection
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function that yields a database session.

    This is the "good taste" approach - single responsibility,
    clean resource management, no special cases.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()  # Explicitly commit on success
        except Exception:
            await session.rollback()  # Rollback on error
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables."""
    from app.models.base import Base

    async with engine.begin() as conn:
        # Import all models to register them with Base
        from app.models.auth.user import User  # noqa: F401
        from app.models.attendance.attendance import Attendance  # noqa: F401
        from app.models.attendance.leave_request import LeaveRequest  # noqa: F401
        from app.models.attendance.makeup_request import MakeupRequest  # noqa: F401
        from app.models.calendar.event import Event  # noqa: F401

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database engine."""
    await engine.dispose()