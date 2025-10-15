"""
JWT token service for authentication.

Design Philosophy:
- Stateless authentication using JWT
- Secure token generation and validation
- Role-based claims
"""

from datetime import datetime, timedelta
from typing import Dict, Optional

from jose import JWTError, jwt

from app.core.config import settings
from app.models.enums import UserRole


class JWTService:
    """JWT token service for authentication."""

    ALGORITHM = "HS256"

    def create_access_token(
        self,
        user_id: int,
        email: str,
        role: UserRole,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a new access token.

        Args:
            user_id: User ID (integer)
            email: User email
            role: User role (can be UserRole enum or string)
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

        # Handle both UserRole enum and string
        role_value = role.value if isinstance(role, UserRole) else role

        to_encode = {
            "sub": str(user_id),  # Subject (user ID as string)
            "email": email,
            "role": role_value,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }

        return jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=self.ALGORITHM
        )

    def verify_token(self, token: str) -> Optional[Dict]:
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
                algorithms=[self.ALGORITHM]
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

    def get_user_id_from_token(self, token: str) -> Optional[int]:
        """Extract user ID from JWT token.

        Args:
            token: JWT token string

        Returns:
            User ID (integer) or None if invalid
        """
        payload = self.verify_token(token)
        if not payload:
            return None

        try:
            return int(payload.get("sub"))
        except (ValueError, TypeError):
            return None

    def get_user_role_from_token(self, token: str) -> Optional[UserRole]:
        """Extract user role from JWT token.

        Args:
            token: JWT token string

        Returns:
            User role or None if invalid
        """
        payload = self.verify_token(token)
        if not payload:
            return None

        try:
            role_str = payload.get("role")
            return UserRole(role_str) if role_str else None
        except (ValueError, TypeError):
            return None