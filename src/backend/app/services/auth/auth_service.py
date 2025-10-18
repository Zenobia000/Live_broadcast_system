"""
Authentication service integrating OAuth and JWT.

Design Philosophy:
- High-level authentication operations
- Integration of OAuth flow with user management
- Secure token handling
"""

import logging
from typing import Dict, Optional, Tuple

from app.models.auth.user import User
from app.models.enums import UserRole
from app.services.auth.jwt_service import JWTService
from app.services.auth.oauth_service import GoogleOAuthService
from app.services.auth.user_service import UserService

logger = logging.getLogger(__name__)


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

    async def get_oauth_authorization_url(self, request) -> Tuple[str, str]:
        """Get Google OAuth authorization URL.

        Args:
            request: Starlette request object

        Returns:
            Tuple of (authorization_url, state)
        """
        return await self.oauth_service.get_authorization_url(request)

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
        from datetime import datetime, timedelta

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
            # Create new user with Google Calendar tokens
            logger.info(f"[Auth] Creating new user for {oauth_data['email']}")
            user = await self.user_service.create_user(
                email=oauth_data['email'],
                google_id=oauth_data['google_id'],
                name=oauth_data['name'],
                avatar_url=oauth_data.get('avatar_url'),
                role=UserRole.MEMBER
            )
            logger.info(f"[Auth] User created successfully: {user.id}")
        else:
            # Update user profile with latest Google data
            logger.info(f"[Auth] Updating existing user: {user.id}")
            user = await self.user_service.update_user_profile(
                user=user,
                name=oauth_data['name'],
                avatar_url=oauth_data.get('avatar_url')
            )

        # Store Google Calendar tokens (refresh token and access token)
        # This enables long-term Calendar API access without re-authentication
        if oauth_data.get('refresh_token'):
            user.google_refresh_token = oauth_data['refresh_token']
            logger.info(f"[Auth] Stored refresh token for Calendar API access")

        user.google_access_token = oauth_data['access_token']
        user.google_token_expires_at = datetime.utcnow() + timedelta(
            seconds=oauth_data.get('expires_in', 3600)
        )
        logger.info(f"[Auth] Stored access token (expires in {oauth_data.get('expires_in', 3600)}s)")

        # Save updated tokens to database
        user = await self.user_service.user_repository.update(user)

        # Generate JWT access token
        logger.info(f"[Auth] Generating JWT token for user: {user.id}")
        logger.info(f"[Auth] User details - ID: {user.id}, Email: {user.email}, Role: {user.role}")

        access_token = self.jwt_service.create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role
        )

        logger.info(f"[Auth] JWT token generated successfully")

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