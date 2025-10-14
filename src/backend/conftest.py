"""
Global pytest configuration and fixtures.
"""

import asyncio
import os
import pytest
from typing import AsyncGenerator, Generator
from unittest.mock import Mock

import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Load test environment variables
from dotenv import load_dotenv
load_dotenv('.env.test')

from app.core.config import settings
from app.main import app
from app.models.base import Base
from app.api.dependencies.auth import get_current_user, get_admin_user
from app.models.auth.user import User
from app.models.enums import UserRole

# Test database configuration
TEST_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def db_session():
    """Create a fresh database session for each test."""
    # Create all tables
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user() -> User:
    """Create a test user for authentication tests."""
    return User(
        id="test-user-123",
        email="test@example.com",
        name="Test User",
        google_id="google-123",
        role=UserRole.USER,
        is_active=True
    )


@pytest.fixture
def test_admin() -> User:
    """Create a test admin user."""
    return User(
        id="test-admin-123",
        email="admin@example.com",
        name="Test Admin",
        google_id="google-admin-123",
        role=UserRole.ADMIN,
        is_active=True
    )


@pytest.fixture
def client():
    """Create a test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def authenticated_client(test_user: User):
    """Create an authenticated test client."""
    def override_get_current_user():
        return test_user

    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as test_client:
        yield test_client

    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def admin_client(test_admin: User):
    """Create an admin authenticated test client."""
    def override_get_current_user():
        return test_admin

    def override_get_admin_user():
        return test_admin

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_admin_user] = override_get_admin_user

    with TestClient(app) as test_client:
        yield test_client

    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def mock_google_oauth():
    """Mock Google OAuth service."""
    mock = Mock()
    mock.exchange_code_for_token.return_value = {
        "access_token": "mock-access-token",
        "id_token": "mock-id-token"
    }
    mock.get_user_info.return_value = {
        "id": "google-123",
        "email": "test@example.com",
        "name": "Test User",
        "picture": "https://example.com/avatar.jpg"
    }
    return mock


@pytest.fixture
def mock_google_calendar():
    """Mock Google Calendar service."""
    mock = Mock()
    mock.get_events.return_value = [
        {
            "id": "event-123",
            "summary": "Test Meeting",
            "start": {"dateTime": "2025-10-14T09:00:00+08:00"},
            "end": {"dateTime": "2025-10-14T10:00:00+08:00"}
        }
    ]
    return mock


@pytest.fixture
def mock_email_service():
    """Mock email notification service."""
    mock = Mock()
    mock.send_notification.return_value = True
    return mock


@pytest.fixture
def mock_slack_service():
    """Mock Slack notification service."""
    mock = Mock()
    mock.send_notification.return_value = True
    return mock


@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment variables."""
    os.environ["TESTING"] = "true"
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
    yield
    # Cleanup
    if "TESTING" in os.environ:
        del os.environ["TESTING"]


# Pytest asyncio configuration
pytest_asyncio.fixture_scope_default = "function"