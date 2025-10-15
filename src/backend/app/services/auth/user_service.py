"""
User service for authentication business logic.

Design Philosophy:
- Service layer handles business logic
- Repository handles data access
- Clean separation of concerns
"""

from typing import Optional

from app.models.auth.user import User
from app.models.enums import UserRole
from app.repositories.auth.user_repository import UserRepository


class UserService:
    """Service for user-related business operations."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def create_user(
        self,
        email: str,
        google_id: str,
        name: str,
        avatar_url: Optional[str] = None,
        role: UserRole = UserRole.MEMBER
    ) -> User:
        """Create a new user.

        Args:
            email: User's email address
            google_id: Google OAuth user ID
            name: User's display name
            avatar_url: User's avatar URL
            role: User role (default: MEMBER)

        Returns:
            Created user

        Raises:
            ValueError: If user already exists
        """
        # Check if user already exists
        if await self.user_repository.exists_by_email(email):
            raise ValueError(f"User with email {email} already exists")

        if await self.user_repository.exists_by_google_id(google_id):
            raise ValueError(f"User with Google ID {google_id} already exists")

        return await self.user_repository.create(
            email=email,
            google_id=google_id,
            name=name,
            avatar_url=avatar_url,
            role=role
        )

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return await self.user_repository.get_by_id(user_id)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return await self.user_repository.get_by_email(email)

    async def get_user_by_google_id(self, google_id: str) -> Optional[User]:
        """Get user by Google ID."""
        return await self.user_repository.get_by_google_id(google_id)

    async def update_user_profile(
        self,
        user: User,
        name: Optional[str] = None,
        avatar_url: Optional[str] = None
    ) -> User:
        """Update user profile information."""
        if name is not None:
            user.name = name
        if avatar_url is not None:
            user.avatar_url = avatar_url

        return await self.user_repository.update(user)

    async def promote_to_admin(self, user: User) -> User:
        """Promote user to admin role."""
        user.role = UserRole.ADMIN
        return await self.user_repository.update(user)

    async def demote_to_member(self, user: User) -> User:
        """Demote user to member role."""
        user.role = UserRole.MEMBER
        return await self.user_repository.update(user)