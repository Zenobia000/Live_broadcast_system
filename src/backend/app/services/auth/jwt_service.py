"""
JWT token service for authentication.

Design Philosophy:
- Stateless authentication using JWT
- Secure token generation and validation
- Role-based claims
"""

from datetime import datetime, timedelta
from typing import Dict, Optional
from uuid import UUID

from jose import JWTError, jwt

from app.core.config import settings
from app.models.enums import UserRole


class JWTService:
    """JWT token service for authentication."""

    ALGORITHM = "HS256"

    @classmethod
    def create_access_token(
        self,
        user_id: UUID,
        email: str,
        role: UserRole,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a new access token.

        Args:
            user_id: User UUID
            email: User email
            role: User role
            expires_delta: Token expiration time delta

        Returns:
            JWT access token string
        """
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        to_encode = {
            "sub": str(user_id),  # Subject (user ID)
            "email": email,
            "role": role.value,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }

        return jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=self.ALGORITHM
        )

    @classmethod
    def verify_token(cls, token: str) -> Optional[Dict]:
        """Verify and decode JWT token.

        Args:
            token: JWT token string

        Returns:
            Decoded token payload or None if invalid
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[cls.ALGORITHM]
            )

            # Verify token type
            if payload.get("type") != "access":
                return None

            # Check expiration
            exp = payload.get("exp")
            if not exp or datetime.fromtimestamp(exp) < datetime.utcnow():
                return None

            return payload

        except JWTError:
            return None

    @classmethod
    def get_user_id_from_token(cls, token: str) -> Optional[UUID]:
        """Extract user ID from JWT token.

        Args:
            token: JWT token string

        Returns:
            User UUID or None if invalid
        """
        payload = cls.verify_token(token)
        if not payload:
            return None

        try:
            return UUID(payload.get("sub"))
        except (ValueError, TypeError):
            return None

    @classmethod
    def get_user_role_from_token(cls, token: str) -> Optional[UserRole]:
        """Extract user role from JWT token.

        Args:
            token: JWT token string

        Returns:
            User role or None if invalid
        """
        payload = cls.verify_token(token)
        if not payload:
            return None

        try:
            role_str = payload.get("role")
            return UserRole(role_str) if role_str else None
        except (ValueError, TypeError):
            return None