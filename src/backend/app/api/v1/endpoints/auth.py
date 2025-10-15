"""
Authentication API endpoints.

Design Philosophy:
- RESTful API design
- Clear error handling
- Secure token management
"""

from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.api.dependencies.auth import AdminUser, AuthService, CurrentUser
from app.api.v1.schemas.user import CurrentUser as CurrentUserSchema
from app.api.v1.schemas.user import RoleUpdate, UserProfile, UserResponse

router = APIRouter()


@router.get("/login/google")
async def google_login(
    request: Request,
    auth_service: AuthService
) -> Dict[str, str]:
    """Initiate Google OAuth login.

    Returns:
        Authorization URL for Google OAuth
    """
    auth_url, state = await auth_service.get_oauth_authorization_url(request)

    return {
        "authorization_url": auth_url,
        "state": state
    }


@router.get("/callback/google")
async def google_callback(
    request: Request,
    code: str,
    state: str,
    auth_service: AuthService
):
    """Handle Google OAuth callback.

    Args:
        request: HTTP request
        code: Authorization code from Google
        state: State parameter for CSRF protection
        auth_service: Authentication service

    Returns:
        Redirect to frontend with token
    """
    try:
        from starlette.responses import RedirectResponse
        import logging

        logger = logging.getLogger(__name__)

        user, access_token = await auth_service.authenticate_with_google(
            request, code, state
        )

        # Redirect to frontend with token
        frontend_url = "http://localhost:3000"
        redirect_url = f"{frontend_url}/auth/callback?token={access_token}"

        logger.info(f"[OAuth Callback] Redirecting to: {redirect_url[:80]}...")
        logger.info(f"[OAuth Callback] Token length: {len(access_token)}")

        return RedirectResponse(url=redirect_url)

    except Exception as e:
        # Redirect to frontend with error
        frontend_url = "http://localhost:3000"
        error_url = f"{frontend_url}/?error={str(e)}"
        return RedirectResponse(url=error_url)


@router.get("/me", response_model=CurrentUserSchema)
async def get_current_user_profile(current_user: CurrentUser):
    """Get current user profile.

    Args:
        current_user: Current authenticated user

    Returns:
        Current user profile with role information
    """
    return CurrentUserSchema.model_validate(current_user)


@router.post("/logout")
async def logout():
    """Logout current user.

    Note: Since we use stateless JWT tokens, logout is handled client-side
    by removing the token. Server-side logout would require token blacklisting.
    """
    return {"message": "Successfully logged out"}


@router.get("/verify")
async def verify_token(auth_service: AuthService, current_user: CurrentUser):
    """Verify current authentication token.

    Args:
        auth_service: Authentication service
        current_user: Current authenticated user

    Returns:
        Token verification status and user info
    """
    return {
        "valid": True,
        "user": UserProfile.model_validate(current_user).model_dump()
    }


@router.put("/users/{user_id}/role", dependencies=[Depends(AdminUser)])
async def update_user_role(
    user_id: str,
    role_update: RoleUpdate,
    auth_service: AuthService,
    admin_user: AdminUser
) -> UserResponse:
    """Update user role (admin only).

    Args:
        user_id: Target user ID
        role_update: New role information
        auth_service: Authentication service
        admin_user: Current admin user

    Returns:
        Updated user information

    Raises:
        HTTPException: If user not found or invalid role
    """
    try:
        user_int_id = int(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )

    user = await auth_service.user_service.get_user_by_id(user_int_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update user role
    user.role = role_update.role
    updated_user = await auth_service.user_service.user_repository.update(user)

    return UserResponse.model_validate(updated_user)