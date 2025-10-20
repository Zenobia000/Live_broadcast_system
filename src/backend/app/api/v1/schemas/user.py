"""
User Pydantic schemas for API input/output validation.

Design Philosophy:
- Separate schemas for request/response to avoid data leakage
- Integer ID for JSON serialization
- Clear validation rules
"""

from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import UserRole


class UserBase(BaseModel):
    """Base user schema with common fields."""

    name: str = Field(..., min_length=1, max_length=100, description="User display name")
    email: EmailStr = Field(..., description="User email address")


class UserCreate(UserBase):
    """Schema for creating a new user."""

    google_id: str = Field(..., min_length=1, max_length=255, description="Google OAuth user ID")
    avatar_url: Optional[str] = Field(None, max_length=512, description="User avatar URL")
    role: UserRole = Field(UserRole.MEMBER, description="User role")


class UserUpdate(BaseModel):
    """Schema for updating user profile."""

    name: Optional[str] = Field(None, min_length=1, max_length=100, description="User display name")
    avatar_url: Optional[str] = Field(None, max_length=512, description="User avatar URL")


class UserResponse(UserBase):
    """Schema for user API responses."""

    id: int = Field(..., description="User ID")
    google_id: str = Field(..., description="Google OAuth user ID")
    avatar_url: Optional[str] = Field(None, description="User avatar URL")
    role: UserRole = Field(..., description="User role")
    created_at: str = Field(..., description="Account creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    """Simplified user profile schema."""

    id: int = Field(..., description="User ID")
    name: str = Field(..., description="User display name")
    email: EmailStr = Field(..., description="User email address")
    avatar_url: Optional[str] = Field(None, description="User avatar URL")
    role: UserRole = Field(..., description="User role")

    class Config:
        from_attributes = True


class CurrentUser(UserProfile):
    """Current authenticated user schema."""

    is_admin: bool = Field(..., description="Whether user has admin privileges")
    is_member: bool = Field(..., description="Whether user is a regular member")

    class Config:
        from_attributes = True


class RoleUpdate(BaseModel):
    """Schema for updating user role (admin only)."""

    role: UserRole = Field(..., description="New user role")


class UserRegisterRequest(BaseModel):
    """Schema for user registration with username/password."""

    name: str = Field(..., min_length=1, max_length=100, description="User display name")
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=100, description="User password (min 8 characters)")


class UserLoginRequest(BaseModel):
    """Schema for user login with username/password."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class AuthResponse(BaseModel):
    """Schema for authentication response."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: UserProfile = Field(..., description="User profile information")