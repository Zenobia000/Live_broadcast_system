"""
Attendance Service Unit Tests
"""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timedelta

from app.services.attendance.attendance_service import AttendanceService
from app.repositories.attendance.attendance_repository import AttendanceRepository
from app.repositories.calendar.event_repository import EventRepository
from app.models.attendance.attendance import Attendance
from app.models.calendar.event import Event
from app.models.auth.user import User
from app.models.enums import AttendanceStatus, UserRole


class TestAttendanceService:
    """Test cases for AttendanceService."""

    @pytest.fixture
    def mock_attendance_repo(self):
        return Mock(spec=AttendanceRepository)

    @pytest.fixture
    def mock_event_repo(self):
        return Mock(spec=EventRepository)

    @pytest.fixture
    def attendance_service(self, mock_attendance_repo, mock_event_repo):
        return AttendanceService(
            attendance_repository=mock_attendance_repo,
            event_repository=mock_event_repo
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
    def sample_event(self):
        return Event(
            id="event-123",
            google_event_id="google-event-123",
            title="Team Meeting",
            start_time=datetime.utcnow() + timedelta(hours=1),
            end_time=datetime.utcnow() + timedelta(hours=2),
            attendees=["test@example.com"],
            location="Conference Room A",
            grace_period_minutes=5
        )

    @pytest.fixture
    def sample_attendance(self, sample_user, sample_event):
        return Attendance(
            id="attendance-123",
            user_id=sample_user.id,
            event_id=sample_event.id,
            status=AttendanceStatus.PRESENT,
            checked_in_at=datetime.utcnow(),
            event_start_time=sample_event.start_time
        )

    @pytest.mark.unit
    @pytest.mark.attendance
    async def test_get_today_status_with_attendance(
        self,
        attendance_service: AttendanceService,
        mock_attendance_repo: Mock,
        mock_event_repo: Mock,
        sample_user: User,
        sample_attendance: Attendance,
        sample_event: Event
    ):
        """Test getting today's status when user has attendance."""
        # Arrange
        today = datetime.utcnow().date()
        mock_attendance_repo.get_today_attendance.return_value = sample_attendance
        mock_event_repo.get_by_id.return_value = sample_event

        # Act
        result = await attendance_service.get_today_status(sample_user.id)

        # Assert
        assert result["is_checked_in"] is True
        assert result["check_in_time"] == sample_attendance.checked_in_at.strftime("%H:%M")
        assert result["event_title"] == sample_event.title
        assert result["status"] == "present"

        # Verify repository calls
        mock_attendance_repo.get_today_attendance.assert_called_once_with(sample_user.id, today)
        mock_event_repo.get_by_id.assert_called_once_with(sample_event.id)

    @pytest.mark.unit
    @pytest.mark.attendance
    async def test_get_today_status_no_attendance(
        self,
        attendance_service: AttendanceService,
        mock_attendance_repo: Mock,
        mock_event_repo: Mock,
        sample_user: User,
        sample_event: Event
    ):
        """Test getting today's status when user has no attendance."""
        # Arrange
        today = datetime.utcnow().date()
        mock_attendance_repo.get_today_attendance.return_value = None
        mock_event_repo.get_next_event.return_value = sample_event

        # Act
        result = await attendance_service.get_today_status(sample_user.id)

        # Assert
        assert result["is_checked_in"] is False
        assert result["next_event_time"] == sample_event.start_time.strftime("%H:%M")
        assert result["status"] == "waiting"

        # Verify repository calls
        mock_attendance_repo.get_today_attendance.assert_called_once_with(sample_user.id, today)
        mock_event_repo.get_next_event.assert_called_once_with(sample_user.email)

    @pytest.mark.unit
    @pytest.mark.attendance
    async def test_auto_check_in_on_time(
        self,
        attendance_service: AttendanceService,
        mock_attendance_repo: Mock,
        mock_event_repo: Mock,
        sample_user: User,
        sample_event: Event
    ):
        """Test automatic check-in when user is on time."""
        # Arrange
        # Event starts in 1 minute (within grace period)
        sample_event.start_time = datetime.utcnow() + timedelta(minutes=1)
        sample_event.grace_period_minutes = 5

        expected_attendance = Attendance(
            user_id=sample_user.id,
            event_id=sample_event.id,
            status=AttendanceStatus.PRESENT,
            checked_in_at=datetime.utcnow(),
            event_start_time=sample_event.start_time
        )

        mock_attendance_repo.get_by_user_and_event.return_value = None  # No existing attendance
        mock_attendance_repo.create.return_value = expected_attendance

        # Act
        result = await attendance_service.auto_check_in(sample_user, sample_event)

        # Assert
        assert result.status == AttendanceStatus.PRESENT
        assert result.user_id == sample_user.id
        assert result.event_id == sample_event.id

        # Verify repository calls
        mock_attendance_repo.get_by_user_and_event.assert_called_once_with(
            sample_user.id, sample_event.id
        )
        mock_attendance_repo.create.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.attendance
    async def test_auto_check_in_late(
        self,
        attendance_service: AttendanceService,
        mock_attendance_repo: Mock,
        sample_user: User,
        sample_event: Event
    ):
        """Test automatic check-in when user is late."""
        # Arrange
        # Event started 10 minutes ago (beyond grace period)
        sample_event.start_time = datetime.utcnow() - timedelta(minutes=10)
        sample_event.grace_period_minutes = 5

        expected_attendance = Attendance(
            user_id=sample_user.id,
            event_id=sample_event.id,
            status=AttendanceStatus.LATE,
            checked_in_at=datetime.utcnow(),
            event_start_time=sample_event.start_time
        )

        mock_attendance_repo.get_by_user_and_event.return_value = None
        mock_attendance_repo.create.return_value = expected_attendance

        # Act
        result = await attendance_service.auto_check_in(sample_user, sample_event)

        # Assert
        assert result.status == AttendanceStatus.LATE
        assert result.user_id == sample_user.id
        assert result.event_id == sample_event.id

    @pytest.mark.unit
    @pytest.mark.attendance
    async def test_auto_check_in_already_exists(
        self,
        attendance_service: AttendanceService,
        mock_attendance_repo: Mock,
        sample_user: User,
        sample_event: Event,
        sample_attendance: Attendance
    ):
        """Test auto check-in when attendance already exists."""
        # Arrange
        mock_attendance_repo.get_by_user_and_event.return_value = sample_attendance

        # Act
        result = await attendance_service.auto_check_in(sample_user, sample_event)

        # Assert
        assert result == sample_attendance

        # Verify no new attendance was created
        mock_attendance_repo.create.assert_not_called()

    @pytest.mark.unit
    @pytest.mark.attendance
    async def test_manual_check_in_success(
        self,
        attendance_service: AttendanceService,
        mock_attendance_repo: Mock,
        mock_event_repo: Mock,
        sample_user: User,
        sample_event: Event
    ):
        """Test manual check-in functionality."""
        # Arrange
        mock_event_repo.get_current_event.return_value = sample_event
        mock_attendance_repo.get_by_user_and_event.return_value = None

        expected_attendance = Attendance(
            user_id=sample_user.id,
            event_id=sample_event.id,
            status=AttendanceStatus.PRESENT,
            checked_in_at=datetime.utcnow(),
            event_start_time=sample_event.start_time
        )

        mock_attendance_repo.create.return_value = expected_attendance

        # Act
        result = await attendance_service.manual_check_in(sample_user.id)

        # Assert
        assert result.status == AttendanceStatus.PRESENT
        assert result.user_id == sample_user.id

        # Verify repository calls
        mock_event_repo.get_current_event.assert_called_once_with(sample_user.email)
        mock_attendance_repo.create.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.attendance
    async def test_manual_check_in_no_current_event(
        self,
        attendance_service: AttendanceService,
        mock_event_repo: Mock,
        sample_user: User
    ):
        """Test manual check-in when no current event exists."""
        # Arrange
        mock_event_repo.get_current_event.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="No current event found for check-in"):
            await attendance_service.manual_check_in(sample_user.id)

    @pytest.mark.unit
    @pytest.mark.attendance
    async def test_get_attendance_history(
        self,
        attendance_service: AttendanceService,
        mock_attendance_repo: Mock,
        sample_user: User
    ):
        """Test getting attendance history."""
        # Arrange
        limit = 10
        expected_history = [sample_attendance for _ in range(5)]
        mock_attendance_repo.get_user_history.return_value = expected_history

        # Act
        result = await attendance_service.get_attendance_history(sample_user.id, limit)

        # Assert
        assert result == expected_history
        assert len(result) == 5

        # Verify repository call
        mock_attendance_repo.get_user_history.assert_called_once_with(sample_user.id, limit)

    @pytest.mark.unit
    @pytest.mark.attendance
    async def test_calculate_late_minutes_on_time(
        self,
        attendance_service: AttendanceService,
        sample_event: Event
    ):
        """Test late calculation when user is on time."""
        # Arrange
        check_in_time = sample_event.start_time - timedelta(minutes=1)  # 1 minute early

        # Act
        late_minutes = attendance_service._calculate_late_minutes(
            check_in_time, sample_event.start_time, sample_event.grace_period_minutes
        )

        # Assert
        assert late_minutes == 0

    @pytest.mark.unit
    @pytest.mark.attendance
    async def test_calculate_late_minutes_within_grace_period(
        self,
        attendance_service: AttendanceService,
        sample_event: Event
    ):
        """Test late calculation within grace period."""
        # Arrange
        check_in_time = sample_event.start_time + timedelta(minutes=3)  # 3 minutes late
        sample_event.grace_period_minutes = 5

        # Act
        late_minutes = attendance_service._calculate_late_minutes(
            check_in_time, sample_event.start_time, sample_event.grace_period_minutes
        )

        # Assert
        assert late_minutes == 0  # Within grace period

    @pytest.mark.unit
    @pytest.mark.attendance
    async def test_calculate_late_minutes_beyond_grace_period(
        self,
        attendance_service: AttendanceService,
        sample_event: Event
    ):
        """Test late calculation beyond grace period."""
        # Arrange
        check_in_time = sample_event.start_time + timedelta(minutes=10)  # 10 minutes late
        sample_event.grace_period_minutes = 5

        # Act
        late_minutes = attendance_service._calculate_late_minutes(
            check_in_time, sample_event.start_time, sample_event.grace_period_minutes
        )

        # Assert
        assert late_minutes == 5  # 10 - 5 (grace period) = 5 minutes late