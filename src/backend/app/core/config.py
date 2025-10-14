"""
Application configuration.

Design Philosophy:
- Environment-based configuration
- Type-safe settings with Pydantic
- Secure defaults
"""

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Application
    APP_NAME: str = "Smart Attendance System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = Field(
        ...,
        description="Database connection URL"
    )

    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6380/0",
        description="Redis connection URL"
    )

    # Security
    SECRET_KEY: str = Field(
        ...,
        min_length=32,
        description="Secret key for JWT signing"
    )

    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=60 * 24,  # 24 hours
        description="Access token expiration time in minutes"
    )

    # Google OAuth 2.0
    GOOGLE_CLIENT_ID: str = Field(
        ...,
        description="Google OAuth 2.0 client ID"
    )

    GOOGLE_CLIENT_SECRET: str = Field(
        ...,
        description="Google OAuth 2.0 client secret"
    )

    GOOGLE_REDIRECT_URI: str = Field(
        default="http://localhost:8000/api/v1/auth/callback/google",
        description="Google OAuth 2.0 redirect URI"
    )

    # CORS
    ALLOWED_ORIGINS: list[str] = Field(
        default=["http://localhost:3000"],
        description="Allowed CORS origins"
    )

    # Google Calendar API
    GOOGLE_CALENDAR_ID: Optional[str] = Field(
        default=None,
        description="Google Calendar ID for event synchronization"
    )

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()