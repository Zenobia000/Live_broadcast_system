"""
Authentication API Integration Tests
"""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.models.auth.user import User
from app.models.enums import UserRole


class TestAuthAPI:
    """Integration tests for authentication API endpoints."""

    @pytest.mark.integration
    @pytest.mark.auth
    def test_health_check_endpoint(self, client: TestClient):
        """Test API health check endpoint."""
        response = client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["version"] == "v1"

    @pytest.mark.integration
    @pytest.mark.auth
    @patch('app.services.auth.oauth_service.GoogleOAuthService.get_user_info')
    @patch('app.services.auth.user_service.UserService.get_user_by_google_id')
    @patch('app.services.auth.user_service.UserService.create_user_from_google')
    def test_google_auth_new_user(
        self,
        mock_create_user,
        mock_get_user,
        mock_get_user_info,
        client: TestClient
    ):
        """Test Google OAuth authentication for new user."""
        # Arrange
        mock_user_info = {
            "id": "google-123456",
            "email": "newuser@example.com",
            "name": "New User",
            "picture": "https://example.com/avatar.jpg"
        }

        new_user = User(
            id="user-456",
            email="newuser@example.com",
            name="New User",
            google_id="google-123456",
            role=UserRole.USER
        )

        mock_get_user_info.return_value = mock_user_info
        mock_get_user.return_value = None  # New user
        mock_create_user.return_value = new_user

        # Act
        response = client.post(
            "/api/v1/auth/google",
            json={"code": "mock-auth-code"}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "token" in data
        assert data["user"]["email"] == "newuser@example.com"
        assert data["user"]["role"] == "user"
        assert data["is_new_user"] is True

    @pytest.mark.integration
    @pytest.mark.auth
    @patch('app.services.auth.oauth_service.GoogleOAuthService.get_user_info')
    @patch('app.services.auth.user_service.UserService.get_user_by_google_id')
    @patch('app.services.auth.user_service.UserService.update_last_login')
    def test_google_auth_existing_user(
        self,
        mock_update_login,
        mock_get_user,
        mock_get_user_info,
        client: TestClient
    ):
        """Test Google OAuth authentication for existing user."""
        # Arrange
        mock_user_info = {
            "id": "google-123456",
            "email": "existing@example.com",
            "name": "Existing User",
            "picture": "https://example.com/avatar.jpg"
        }

        existing_user = User(
            id="user-789",
            email="existing@example.com",
            name="Existing User",
            google_id="google-123456",
            role=UserRole.USER
        )

        mock_get_user_info.return_value = mock_user_info
        mock_get_user.return_value = existing_user
        mock_update_login.return_value = existing_user

        # Act
        response = client.post(
            "/api/v1/auth/google",
            json={"code": "mock-auth-code"}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "token" in data
        assert data["user"]["email"] == "existing@example.com"
        assert data["is_new_user"] is False

        # Verify last login was updated
        mock_update_login.assert_called_once()

    @pytest.mark.integration
    @pytest.mark.auth
    def test_google_auth_missing_code(self, client: TestClient):
        """Test Google OAuth without authorization code."""
        response = client.post(
            "/api/v1/auth/google",
            json={}
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.integration
    @pytest.mark.auth
    @patch('app.services.auth.oauth_service.GoogleOAuthService.get_user_info')
    def test_google_auth_invalid_code(
        self,
        mock_get_user_info,
        client: TestClient
    ):
        """Test Google OAuth with invalid authorization code."""
        # Arrange
        mock_get_user_info.side_effect = Exception("Invalid authorization code")

        # Act
        response = client.post(
            "/api/v1/auth/google",
            json={"code": "invalid-code"}
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Google authentication failed"

    @pytest.mark.integration
    @pytest.mark.auth
    def test_get_current_user_authenticated(self, authenticated_client: TestClient, test_user: User):
        """Test getting current user profile with valid token."""
        response = authenticated_client.get("/api/v1/users/me")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
        assert data["name"] == test_user.name

    @pytest.mark.integration
    @pytest.mark.auth
    def test_get_current_user_unauthenticated(self, client: TestClient):
        """Test getting current user without authentication."""
        response = client.get("/api/v1/users/me")

        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.auth
    def test_logout_authenticated_user(self, authenticated_client: TestClient):
        """Test logout with authenticated user."""
        response = authenticated_client.post("/api/v1/auth/logout")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Successfully logged out"

    @pytest.mark.integration
    @pytest.mark.auth
    def test_logout_unauthenticated_user(self, client: TestClient):
        """Test logout without authentication."""
        response = client.post("/api/v1/auth/logout")

        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.auth
    def test_admin_only_endpoint_with_admin(self, admin_client: TestClient):
        """Test admin-only endpoint with admin user."""
        response = admin_client.get("/api/v1/admin/requests/pending")

        # Should succeed (200) or return empty data depending on implementation
        assert response.status_code in [200, 404]

    @pytest.mark.integration
    @pytest.mark.auth
    def test_admin_only_endpoint_with_regular_user(self, authenticated_client: TestClient):
        """Test admin-only endpoint with regular user."""
        response = authenticated_client.get("/api/v1/admin/requests/pending")

        assert response.status_code == 403  # Forbidden

    @pytest.mark.integration
    @pytest.mark.auth
    def test_admin_only_endpoint_unauthenticated(self, client: TestClient):
        """Test admin-only endpoint without authentication."""
        response = client.get("/api/v1/admin/requests/pending")

        assert response.status_code == 401  # Unauthorized

    @pytest.mark.integration
    @pytest.mark.auth
    @patch('app.services.auth.user_service.UserService.update_user_role')
    def test_update_user_role_as_admin(
        self,
        mock_update_role,
        admin_client: TestClient,
        test_admin: User
    ):
        """Test updating user role as admin."""
        # Arrange
        target_user_id = "user-123"
        new_role = "admin"

        updated_user = User(
            id=target_user_id,
            email="user@example.com",
            name="User",
            role=UserRole.ADMIN
        )
        mock_update_role.return_value = updated_user

        # Act
        response = admin_client.put(
            f"/api/v1/users/{target_user_id}/role",
            json={"role": new_role}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "admin"

        # Verify service was called
        mock_update_role.assert_called_once()

    @pytest.mark.integration
    @pytest.mark.auth
    def test_update_user_role_as_regular_user(self, authenticated_client: TestClient):
        """Test updating user role as regular user (should fail)."""
        response = authenticated_client.put(
            "/api/v1/users/user-123/role",
            json={"role": "admin"}
        )

        assert response.status_code == 403  # Forbidden