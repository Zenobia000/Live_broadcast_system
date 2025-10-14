"""
Authentication Service Unit Tests
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

from app.services.auth.auth_service import AuthService
from app.services.auth.user_service import UserService
from app.services.auth.oauth_service import GoogleOAuthService
from app.services.auth.jwt_service import JWTService
from app.models.auth.user import User
from app.models.enums import UserRole


class TestAuthService:
    """Test cases for AuthService."""

    @pytest.fixture
    def mock_user_service(self):
        return Mock(spec=UserService)

    @pytest.fixture
    def mock_oauth_service(self):
        return Mock(spec=GoogleOAuthService)

    @pytest.fixture
    def mock_jwt_service(self):
        return Mock(spec=JWTService)

    @pytest.fixture
    def auth_service(self, mock_user_service, mock_oauth_service, mock_jwt_service):
        return AuthService(
            user_service=mock_user_service,
            oauth_service=mock_oauth_service,
            jwt_service=mock_jwt_service
        )

    @pytest.fixture
    def sample_google_user_info(self):
        return {
            "id": "google-123456",
            "email": "test@example.com",
            "name": "Test User",
            "picture": "https://example.com/avatar.jpg"
        }

    @pytest.fixture
    def sample_user(self):
        return User(
            id="user-123",
            email="test@example.com",
            name="Test User",
            google_id="google-123456",
            role=UserRole.USER,
            is_active=True
        )

    @pytest.mark.unit
    @pytest.mark.auth
    async def test_authenticate_with_google_new_user(
        self,
        auth_service: AuthService,
        mock_oauth_service: Mock,
        mock_user_service: Mock,
        mock_jwt_service: Mock,
        sample_google_user_info: dict,
        sample_user: User
    ):
        """Test Google authentication for new user."""
        # Arrange
        access_token = "mock-access-token"
        expected_jwt_token = "jwt-token-123"

        mock_oauth_service.get_user_info.return_value = sample_google_user_info
        mock_user_service.get_user_by_google_id.return_value = None  # New user
        mock_user_service.create_user_from_google.return_value = sample_user
        mock_jwt_service.create_access_token.return_value = expected_jwt_token

        # Act
        result = await auth_service.authenticate_with_google(access_token)

        # Assert
        assert result["success"] is True
        assert result["token"] == expected_jwt_token
        assert result["user"] == sample_user
        assert result["is_new_user"] is True

        # Verify service calls
        mock_oauth_service.get_user_info.assert_called_once_with(access_token)
        mock_user_service.get_user_by_google_id.assert_called_once_with("google-123456")
        mock_user_service.create_user_from_google.assert_called_once_with(sample_google_user_info)
        mock_jwt_service.create_access_token.assert_called_once_with({"sub": sample_user.id})

    @pytest.mark.unit
    @pytest.mark.auth
    async def test_authenticate_with_google_existing_user(
        self,
        auth_service: AuthService,
        mock_oauth_service: Mock,
        mock_user_service: Mock,
        mock_jwt_service: Mock,
        sample_google_user_info: dict,
        sample_user: User
    ):
        """Test Google authentication for existing user."""
        # Arrange
        access_token = "mock-access-token"
        expected_jwt_token = "jwt-token-123"

        mock_oauth_service.get_user_info.return_value = sample_google_user_info
        mock_user_service.get_user_by_google_id.return_value = sample_user  # Existing user
        mock_user_service.update_last_login.return_value = sample_user
        mock_jwt_service.create_access_token.return_value = expected_jwt_token

        # Act
        result = await auth_service.authenticate_with_google(access_token)

        # Assert
        assert result["success"] is True
        assert result["token"] == expected_jwt_token
        assert result["user"] == sample_user
        assert result["is_new_user"] is False

        # Verify service calls
        mock_oauth_service.get_user_info.assert_called_once_with(access_token)
        mock_user_service.get_user_by_google_id.assert_called_once_with("google-123456")
        mock_user_service.update_last_login.assert_called_once_with(sample_user.id)
        mock_jwt_service.create_access_token.assert_called_once_with({"sub": sample_user.id})

    @pytest.mark.unit
    @pytest.mark.auth
    async def test_authenticate_with_google_invalid_token(
        self,
        auth_service: AuthService,
        mock_oauth_service: Mock,
        mock_user_service: Mock,
        mock_jwt_service: Mock
    ):
        """Test Google authentication with invalid token."""
        # Arrange
        access_token = "invalid-token"
        mock_oauth_service.get_user_info.side_effect = Exception("Invalid token")

        # Act & Assert
        with pytest.raises(Exception, match="Invalid token"):
            await auth_service.authenticate_with_google(access_token)

        # Verify only OAuth service was called
        mock_oauth_service.get_user_info.assert_called_once_with(access_token)
        mock_user_service.get_user_by_google_id.assert_not_called()
        mock_jwt_service.create_access_token.assert_not_called()

    @pytest.mark.unit
    @pytest.mark.auth
    async def test_validate_token_valid(
        self,
        auth_service: AuthService,
        mock_jwt_service: Mock,
        mock_user_service: Mock,
        sample_user: User
    ):
        """Test token validation with valid token."""
        # Arrange
        token = "valid-jwt-token"
        payload = {"sub": "user-123", "exp": datetime.utcnow() + timedelta(hours=1)}

        mock_jwt_service.decode_token.return_value = payload
        mock_user_service.get_user_by_id.return_value = sample_user

        # Act
        result = await auth_service.validate_token(token)

        # Assert
        assert result == sample_user

        # Verify service calls
        mock_jwt_service.decode_token.assert_called_once_with(token)
        mock_user_service.get_user_by_id.assert_called_once_with("user-123")

    @pytest.mark.unit
    @pytest.mark.auth
    async def test_validate_token_expired(
        self,
        auth_service: AuthService,
        mock_jwt_service: Mock,
        mock_user_service: Mock
    ):
        """Test token validation with expired token."""
        # Arrange
        token = "expired-jwt-token"
        mock_jwt_service.decode_token.side_effect = Exception("Token expired")

        # Act & Assert
        with pytest.raises(Exception, match="Token expired"):
            await auth_service.validate_token(token)

        # Verify service calls
        mock_jwt_service.decode_token.assert_called_once_with(token)
        mock_user_service.get_user_by_id.assert_not_called()

    @pytest.mark.unit
    @pytest.mark.auth
    async def test_validate_token_user_not_found(
        self,
        auth_service: AuthService,
        mock_jwt_service: Mock,
        mock_user_service: Mock
    ):
        """Test token validation when user doesn't exist."""
        # Arrange
        token = "valid-jwt-token"
        payload = {"sub": "non-existent-user", "exp": datetime.utcnow() + timedelta(hours=1)}

        mock_jwt_service.decode_token.return_value = payload
        mock_user_service.get_user_by_id.return_value = None

        # Act & Assert
        result = await auth_service.validate_token(token)
        assert result is None

        # Verify service calls
        mock_jwt_service.decode_token.assert_called_once_with(token)
        mock_user_service.get_user_by_id.assert_called_once_with("non-existent-user")

    @pytest.mark.unit
    @pytest.mark.auth
    async def test_refresh_token_valid_user(
        self,
        auth_service: AuthService,
        mock_jwt_service: Mock,
        sample_user: User
    ):
        """Test token refresh for valid user."""
        # Arrange
        expected_new_token = "new-jwt-token"
        mock_jwt_service.create_access_token.return_value = expected_new_token

        # Act
        result = await auth_service.refresh_token(sample_user)

        # Assert
        assert result == expected_new_token

        # Verify service call
        mock_jwt_service.create_access_token.assert_called_once_with({"sub": sample_user.id})

    @pytest.mark.unit
    @pytest.mark.auth
    async def test_logout_user(
        self,
        auth_service: AuthService,
        mock_jwt_service: Mock,
        sample_user: User
    ):
        """Test user logout."""
        # Arrange
        token = "user-token"

        # Act
        result = await auth_service.logout_user(sample_user, token)

        # Assert
        assert result["success"] is True
        assert result["message"] == "Successfully logged out"

        # Verify service call (if token blacklisting is implemented)
        # mock_jwt_service.blacklist_token.assert_called_once_with(token)

    @pytest.mark.unit
    @pytest.mark.auth
    async def test_update_user_role_admin_only(
        self,
        auth_service: AuthService,
        mock_user_service: Mock,
        test_admin: User,
        sample_user: User
    ):
        """Test role update functionality (admin only)."""
        # Arrange
        new_role = UserRole.ADMIN
        updated_user = User(
            **sample_user.__dict__,
            role=new_role
        )
        mock_user_service.update_user_role.return_value = updated_user

        # Act
        result = await auth_service.update_user_role(
            admin_user=test_admin,
            target_user_id=sample_user.id,
            new_role=new_role
        )

        # Assert
        assert result == updated_user

        # Verify service call
        mock_user_service.update_user_role.assert_called_once_with(sample_user.id, new_role)

    @pytest.mark.unit
    @pytest.mark.auth
    async def test_update_user_role_non_admin_forbidden(
        self,
        auth_service: AuthService,
        mock_user_service: Mock,
        sample_user: User  # Regular user, not admin
    ):
        """Test that non-admin users cannot update roles."""
        # Act & Assert
        with pytest.raises(PermissionError, match="Only admin users can update roles"):
            await auth_service.update_user_role(
                admin_user=sample_user,  # Not an admin
                target_user_id="other-user-123",
                new_role=UserRole.ADMIN
            )

        # Verify user service was never called
        mock_user_service.update_user_role.assert_not_called()