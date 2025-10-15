"""
User repository for database operations.

Design Philosophy (Linus Torvalds - "Good Taste"):
- Repository pattern isolates database concerns
- Clean interface for data access operations
- No business logic here - pure data operations
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth.user import User
from app.models.enums import UserRole


class UserRepository:
    """Repository for User model database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        email: str,
        google_id: str,
        name: str,
        avatar_url: Optional[str] = None,
        role: UserRole = UserRole.MEMBER
    ) -> User:
        """Create a new user."""
        user = User(
            email=email,
            google_id=google_id,
            name=name,
            avatar_url=avatar_url,
            role=role
        )
        self.session.add(user)
        await self.session.flush()  # Flush to get the ID without committing
        await self.session.refresh(user)  # Refresh to get generated fields
        return user

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_google_id(self, google_id: str) -> Optional[User]:
        """Get user by Google ID."""
        result = await self.session.execute(
            select(User).where(User.google_id == google_id)
        )
        return result.scalar_one_or_none()

    async def update(self, user: User) -> User:
        """Update user information."""
        await self.session.flush()  # Flush changes without committing
        await self.session.refresh(user)
        return user

    async def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email."""
        result = await self.session.execute(
            select(User.id).where(User.email == email)
        )
        return result.scalar_one_or_none() is not None

    async def exists_by_google_id(self, google_id: str) -> bool:
        """Check if user exists by Google ID."""
        result = await self.session.execute(
            select(User.id).where(User.google_id == google_id)
        )
        return result.scalar_one_or_none() is not None