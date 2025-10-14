"""
Authentication and authorization dependencies for FastAPI.

Design Philosophy:
- Dependency injection for clean API design
- Role-based access control (RBAC)
- Secure token extraction from headers
"""

from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.models.auth.user import User
from app.models.enums import UserRole
from app.services.auth.auth_service import AuthService

# HTTP Bearer token security scheme
security = HTTPBearer()


async def get_auth_service() -> AuthService:
    """Get authentication service instance."""
    # This will be implemented with dependency injection container
    # For now, create instances directly
    from app.repositories.auth.user_repository import UserRepository
    from app.services.auth.user_service import UserService
    from app.services.auth.oauth_service import GoogleOAuthService
    from app.services.auth.jwt_service import JWTService

    # Note: In production, these would come from a dependency container
    user_repository = UserRepository(session=None)  # Session will be injected
    user_service = UserService(user_repository)
    oauth_service = GoogleOAuthService()
    jwt_service = JWTService()

    return AuthService(user_service, oauth_service, jwt_service)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> User:
    """Get current authenticated user.

    Args:
        credentials: HTTP Bearer token credentials
        auth_service: Authentication service

    Returns:
        Current user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials

    # Verify token and get user
    user = await auth_service.get_current_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """Get current active user.

    Args:
        current_user: Current authenticated user

    Returns:
        Current active user

    Raises:
        HTTPException: If user is inactive (for future implementation)
    """
    # For now, all users are active
    # In the future, we might add user activation/deactivation
    return current_user


async def get_current_admin_user(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    """Get current admin user.

    Args:
        current_user: Current authenticated user

    Returns:
        Current admin user

    Raises:
        HTTPException: If user doesn't have admin privileges
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    return current_user


def require_role(required_role: UserRole):
    """Dependency factory for role-based access control.

    Args:
        required_role: Required user role

    Returns:
        Dependency function that checks user role
    """
    async def check_role(
        current_user: Annotated[User, Depends(get_current_active_user)]
    ) -> User:
        """Check if user has required role."""
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role: {required_role.value}"
            )
        return current_user

    return check_role


def require_admin():
    """Dependency for admin-only endpoints."""
    return require_role(UserRole.ADMIN)


def require_member_or_admin():
    """Dependency for member or admin endpoints."""
    async def check_member_or_admin(
        current_user: Annotated[User, Depends(get_current_active_user)]
    ) -> User:
        """Check if user is member or admin."""
        if current_user.role not in [UserRole.MEMBER, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Member or admin privileges required"
            )
        return current_user

    return check_member_or_admin


# Common dependencies for easy import
CurrentUser = Annotated[User, Depends(get_current_active_user)]
AdminUser = Annotated[User, Depends(get_current_admin_user)]
AuthService = Annotated[AuthService, Depends(get_auth_service)]