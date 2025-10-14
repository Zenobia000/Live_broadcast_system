"""
Leave Service Unit Tests
"""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime, date, timedelta

from app.services.attendance.leave_service import LeaveService
from app.repositories.attendance.leave_request_repository import LeaveRequestRepository
from app.services.notification.notification_service import NotificationService
from app.models.attendance.leave_request import LeaveRequest
from app.models.auth.user import User
from app.models.enums import LeaveRequestStatus, LeaveType, UserRole


class TestLeaveService:
    """Test cases for LeaveService."""

    @pytest.fixture
    def mock_leave_repo(self):
        return Mock(spec=LeaveRequestRepository)

    @pytest.fixture
    def mock_notification_service(self):
        return Mock(spec=NotificationService)

    @pytest.fixture
    def leave_service(self, mock_leave_repo, mock_notification_service):
        return LeaveService(
            leave_repository=mock_leave_repo,
            notification_service=mock_notification_service
        )

    @pytest.fixture
    def sample_user(self):
        return User(
            id="user-123",
            email="test@example.com",
            name="Test User",
            google_id="google-123",
            role=UserRole.USER
        )

    @pytest.fixture
    def sample_leave_request(self, sample_user):
        return LeaveRequest(
            id="leave-123",
            user_id=sample_user.id,
            start_date=date.today() + timedelta(days=1),
            end_date=date.today() + timedelta(days=1),
            type=LeaveType.FULL_DAY,
            reason="Personal affairs",
            description="Family event",
            status=LeaveRequestStatus.PENDING
        )

    @pytest.mark.unit
    @pytest.mark.requests
    async def test_submit_leave_request_success(
        self,
        leave_service: LeaveService,
        mock_leave_repo: Mock,
        mock_notification_service: Mock,
        sample_user: User,
        sample_leave_request: LeaveRequest
    ):
        """Test successful leave request submission."""
        # Arrange
        leave_data = {
            "start_date": sample_leave_request.start_date,
            "end_date": sample_leave_request.end_date,
            "type": sample_leave_request.type,
            "reason": sample_leave_request.reason,
            "description": sample_leave_request.description
        }

        mock_leave_repo.has_overlapping_request.return_value = False
        mock_leave_repo.create.return_value = sample_leave_request
        mock_notification_service.send_leave_request_submitted = AsyncMock()

        # Act
        result = await leave_service.submit_leave_request(sample_user, leave_data)

        # Assert
        assert result.id == sample_leave_request.id
        assert result.status == LeaveRequestStatus.PENDING
        assert result.user_id == sample_user.id

        # Verify repository calls
        mock_leave_repo.has_overlapping_request.assert_called_once_with(
            sample_user.id, leave_data["start_date"], leave_data["end_date"]
        )
        mock_leave_repo.create.assert_called_once()

        # Verify notification sent
        mock_notification_service.send_leave_request_submitted.assert_called_once_with(
            user=sample_user,
            leave_request=sample_leave_request
        )

    @pytest.mark.unit
    @pytest.mark.requests
    async def test_submit_leave_request_overlapping_dates(
        self,
        leave_service: LeaveService,
        mock_leave_repo: Mock,
        sample_user: User,
        sample_leave_request: LeaveRequest
    ):
        """Test leave request submission with overlapping dates."""
        # Arrange
        leave_data = {
            "start_date": sample_leave_request.start_date,
            "end_date": sample_leave_request.end_date,
            "type": sample_leave_request.type,
            "reason": sample_leave_request.reason
        }

        mock_leave_repo.has_overlapping_request.return_value = True

        # Act & Assert
        with pytest.raises(ValueError, match="Overlapping leave request exists"):
            await leave_service.submit_leave_request(sample_user, leave_data)

        # Verify repository was checked but no creation happened
        mock_leave_repo.has_overlapping_request.assert_called_once()
        mock_leave_repo.create.assert_not_called()

    @pytest.mark.unit
    @pytest.mark.requests
    async def test_submit_leave_request_past_date(
        self,
        leave_service: LeaveService,
        mock_leave_repo: Mock,
        sample_user: User
    ):
        """Test leave request submission with past date."""
        # Arrange
        leave_data = {
            "start_date": date.today() - timedelta(days=1),  # Yesterday
            "end_date": date.today() - timedelta(days=1),
            "type": LeaveType.FULL_DAY,
            "reason": "Personal affairs"
        }

        # Act & Assert
        with pytest.raises(ValueError, match="Cannot submit leave request for past dates"):
            await leave_service.submit_leave_request(sample_user, leave_data)

        # Verify no repository calls were made
        mock_leave_repo.has_overlapping_request.assert_not_called()
        mock_leave_repo.create.assert_not_called()

    @pytest.mark.unit
    @pytest.mark.requests
    async def test_get_user_leave_requests(
        self,
        leave_service: LeaveService,
        mock_leave_repo: Mock,
        sample_user: User,
        sample_leave_request: LeaveRequest
    ):
        """Test getting user's leave requests."""
        # Arrange
        expected_requests = [sample_leave_request]
        mock_leave_repo.get_by_user_id.return_value = expected_requests

        # Act
        result = await leave_service.get_user_leave_requests(
            sample_user.id,
            status=LeaveRequestStatus.PENDING
        )

        # Assert
        assert result == expected_requests
        assert len(result) == 1

        # Verify repository call
        mock_leave_repo.get_by_user_id.assert_called_once_with(
            sample_user.id,
            status=LeaveRequestStatus.PENDING
        )

    @pytest.mark.unit
    @pytest.mark.requests
    async def test_update_leave_request_status_approve(
        self,
        leave_service: LeaveService,
        mock_leave_repo: Mock,
        mock_notification_service: Mock,
        sample_user: User,
        sample_leave_request: LeaveRequest
    ):
        """Test approving leave request."""
        # Arrange
        admin_user = User(id="admin-123", role=UserRole.ADMIN, email="admin@example.com", name="Admin User")
        approved_request = LeaveRequest(**sample_leave_request.__dict__)
        approved_request.status = LeaveRequestStatus.APPROVED
        approved_request.reviewed_by = admin_user.id
        approved_request.reviewed_at = datetime.utcnow()

        mock_leave_repo.get_by_id.return_value = sample_leave_request
        mock_leave_repo.update.return_value = approved_request
        mock_notification_service.send_leave_request_reviewed = AsyncMock()

        # Act
        result = await leave_service.update_leave_request_status(
            request_id=sample_leave_request.id,
            status=LeaveRequestStatus.APPROVED,
            reviewed_by=admin_user,
            comment="Approved for personal affairs"
        )

        # Assert
        assert result.status == LeaveRequestStatus.APPROVED
        assert result.reviewed_by == admin_user.id

        # Verify repository calls
        mock_leave_repo.get_by_id.assert_called_once_with(sample_leave_request.id)
        mock_leave_repo.update.assert_called_once()

        # Verify notification sent
        mock_notification_service.send_leave_request_reviewed.assert_called_once_with(
            user=sample_user,
            leave_request=approved_request,
            reviewer=admin_user
        )

    @pytest.mark.unit
    @pytest.mark.requests
    async def test_update_leave_request_not_found(
        self,
        leave_service: LeaveService,
        mock_leave_repo: Mock,
        sample_user: User
    ):
        """Test updating non-existent leave request."""
        # Arrange
        admin_user = User(id="admin-123", role=UserRole.ADMIN, email="admin@example.com", name="Admin User")
        mock_leave_repo.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Leave request not found"):
            await leave_service.update_leave_request_status(
                request_id="non-existent-123",
                status=LeaveRequestStatus.APPROVED,
                reviewed_by=admin_user
            )

        # Verify only get was called
        mock_leave_repo.get_by_id.assert_called_once_with("non-existent-123")
        mock_leave_repo.update.assert_not_called()

    @pytest.mark.unit
    @pytest.mark.requests
    async def test_cancel_leave_request_success(
        self,
        leave_service: LeaveService,
        mock_leave_repo: Mock,
        sample_user: User,
        sample_leave_request: LeaveRequest
    ):
        """Test cancelling leave request."""
        # Arrange
        mock_leave_repo.get_by_id.return_value = sample_leave_request

        cancelled_request = LeaveRequest(**sample_leave_request.__dict__)
        cancelled_request.status = LeaveRequestStatus.CANCELLED

        mock_leave_repo.update.return_value = cancelled_request

        # Act
        result = await leave_service.cancel_leave_request(
            request_id=sample_leave_request.id,
            user_id=sample_user.id
        )

        # Assert
        assert result.status == LeaveRequestStatus.CANCELLED

        # Verify repository calls
        mock_leave_repo.get_by_id.assert_called_once_with(sample_leave_request.id)
        mock_leave_repo.update.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.requests
    async def test_cancel_leave_request_unauthorized(
        self,
        leave_service: LeaveService,
        mock_leave_repo: Mock,
        sample_leave_request: LeaveRequest
    ):
        """Test cancelling leave request by unauthorized user."""
        # Arrange
        other_user_id = "other-user-456"
        mock_leave_repo.get_by_id.return_value = sample_leave_request

        # Act & Assert
        with pytest.raises(PermissionError, match="User can only cancel their own requests"):
            await leave_service.cancel_leave_request(
                request_id=sample_leave_request.id,
                user_id=other_user_id
            )

        # Verify no update was called
        mock_leave_repo.update.assert_not_called()