"""
Authentication service integrating OAuth and JWT.

Design Philosophy:
- High-level authentication operations
- Integration of OAuth flow with user management
- Secure token handling
"""

from typing import Dict, Optional, Tuple

from app.models.auth.user import User
from app.models.enums import UserRole
from app.services.auth.jwt_service import JWTService
from app.services.auth.oauth_service import GoogleOAuthService
from app.services.auth.user_service import UserService


class AuthService:
    """Authentication service."""

    def __init__(
        self,
        user_service: UserService,
        oauth_service: GoogleOAuthService,
        jwt_service: JWTService
    ):
        self.user_service = user_service
        self.oauth_service = oauth_service
        self.jwt_service = jwt_service

    def get_oauth_authorization_url(self, request) -> Tuple[str, str]:
        """Get Google OAuth authorization URL.

        Args:
            request: Starlette request object

        Returns:
            Tuple of (authorization_url, state)
        """
        return self.oauth_service.get_authorization_url(request)

    async def authenticate_with_google(
        self, request, code: str, state: str
    ) -> Tuple[User, str]:
        """Authenticate user with Google OAuth.

        Args:
            request: Starlette request object
            code: OAuth authorization code
            state: OAuth state parameter

        Returns:
            Tuple of (user, access_token)

        Raises:
            Exception: If authentication fails
        """
        # Exchange code for token and get user info
        oauth_data = await self.oauth_service.exchange_code_for_token(
            request, code, state
        )

        # Check if user exists
        user = await self.user_service.get_user_by_google_id(
            oauth_data['google_id']
        )

        if not user:
            # Check by email (in case Google ID changed)
            user = await self.user_service.get_user_by_email(
                oauth_data['email']
            )

        if not user:
            # Create new user
            user = await self.user_service.create_user(
                email=oauth_data['email'],
                google_id=oauth_data['google_id'],
                name=oauth_data['name'],
                avatar_url=oauth_data.get('avatar_url'),
                role=UserRole.MEMBER
            )
        else:
            # Update user profile with latest Google data
            user = await self.user_service.update_user_profile(
                user=user,
                name=oauth_data['name'],
                avatar_url=oauth_data.get('avatar_url')
            )

        # Generate JWT access token
        access_token = self.jwt_service.create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role
        )

        return user, access_token

    async def get_current_user(self, token: str) -> Optional[User]:
        """Get current user from JWT token.

        Args:
            token: JWT access token

        Returns:
            User object or None if invalid
        """
        user_id = self.jwt_service.get_user_id_from_token(token)
        if not user_id:
            return None

        return await self.user_service.get_user_by_id(user_id)

    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token.

        Args:
            token: JWT access token

        Returns:
            Token payload or None if invalid
        """
        return self.jwt_service.verify_token(token)

    def create_token_for_user(self, user: User) -> str:
        """Create JWT token for existing user.

        Args:
            user: User object

        Returns:
            JWT access token
        """
        return self.jwt_service.create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role
        )