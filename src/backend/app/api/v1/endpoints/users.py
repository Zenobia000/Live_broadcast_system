"""
User API endpoints.

Design Philosophy:
- RESTful API design for user profile management
- Secure access to user data
- Profile update functionality
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import CurrentUser
from app.core.database import get_session as get_db_session
from app.models.auth.user import User

router = APIRouter()


class UserResponse(BaseModel):
    """User response schema."""
    id: str
    email: str
    name: str
    avatar: Optional[str] = None
    role: str
    createdAt: str
    updatedAt: str


class UserUpdateRequest(BaseModel):
    """User update request schema."""
    name: Optional[str] = None
    avatar: Optional[str] = None


@router.get("/me", response_model=dict)
async def get_current_user(current_user: CurrentUser):
    """Get current user profile.

    Returns:
        Current user information
    """
    return {
        "success": True,
        "data": {
            "id": str(current_user.id),
            "email": current_user.email,
            "name": current_user.name,
            "avatar": current_user.avatar_url,
            "role": current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
            "createdAt": current_user.created_at.isoformat(),
            "updatedAt": current_user.updated_at.isoformat()
        }
    }


@router.put("/me")
async def update_current_user(
    update_data: UserUpdateRequest,
    current_user: CurrentUser
):
    """Update current user profile.

    Args:
        update_data: User profile update data
        current_user: Current authenticated user

    Returns:
        Updated user information
    """
    # TODO: Implement profile update logic
    # For now, return current user data
    return {
        "success": True,
        "data": {
            "id": str(current_user.id),
            "email": current_user.email,
            "name": update_data.name or current_user.name,
            "avatar": update_data.avatar or current_user.avatar_url,
            "role": current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
            "createdAt": current_user.created_at.isoformat(),
            "updatedAt": current_user.updated_at.isoformat()
        },
        "message": "Profile update functionality will be fully implemented in next phase"
    }


@router.get("", response_model=dict)
async def get_all_users(
    db: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = None
):
    """Get all users in the system.

    This endpoint is used for selecting participants when creating events.

    Returns:
        List of all users
    """
    result = await db.execute(select(User))
    users = result.scalars().all()

    return {
        "success": True,
        "data": [
            {
                "id": str(user.id),
                "email": user.email,
                "name": user.name,
                "avatar": user.avatar_url,
                "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
                "createdAt": user.created_at.isoformat(),
                "updatedAt": user.updated_at.isoformat()
            }
            for user in users
        ]
    }
