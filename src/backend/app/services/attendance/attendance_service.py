"""
Attendance service for event-driven check-in logic.

Design Philosophy (Linus: "Good Taste"):
- Event-driven: Check-in triggered by calendar events
- Smart late detection: Grace period per event
- Single status transitions: Eliminate special cases
"""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from app.models.attendance.attendance import Attendance
from app.models.calendar.event import Event
from app.models.enums import AttendanceStatus
from app.repositories.attendance.attendance_repository import AttendanceRepository
from app.repositories.calendar.event_repository import EventRepository


class AttendanceService:
    """Service for attendance management and check-in logic."""

    def __init__(
        self,
        attendance_repository: AttendanceRepository,
        event_repository: EventRepository
    ):
        self.attendance_repository = attendance_repository
        self.event_repository = event_repository

    async def auto_check_in_user(
        self, user_id: UUID, current_time: Optional[datetime] = None
    ) -> List[Attendance]:
        """Automatically check in user for ongoing events.

        Args:
            user_id: User ID to check in
            current_time: Current time (default: now)

        Returns:
            List of updated attendance records

        This is the core event-driven check-in logic:
        1. Find ongoing events
        2. Check if user has attendance records
        3. Determine if check-in is late based on grace period
        4. Update attendance status
        """
        if current_time is None:
            current_time = datetime.utcnow()

        # Get currently ongoing events
        ongoing_events = await self.event_repository.list_ongoing_events(current_time)

        checked_in_attendances = []

        for event in ongoing_events:
            # Check if user already has attendance for this event
            existing_attendance = await self.attendance_repository.get_by_user_and_event(
                user_id, event.id
            )

            # Skip if already checked in
            if existing_attendance and existing_attendance.is_present_or_late:
                continue

            # Determine if check-in is late
            is_late = event.is_late_checkin(current_time)

            # Check in user
            attendance = await self.attendance_repository.check_in_user(
                user_id=user_id,
                event_id=event.id,
                check_in_time=current_time,
                is_late=is_late
            )

            checked_in_attendances.append(attendance)

        return checked_in_attendances

    async def manual_check_in(
        self,
        user_id: UUID,
        event_id: UUID,
        check_in_time: Optional[datetime] = None
    ) -> Attendance:
        """Manual check-in for specific event.

        Args:
            user_id: User ID
            event_id: Event ID
            check_in_time: Check-in time (default: now)

        Returns:
            Updated attendance record

        Raises:
            ValueError: If event not found or invalid check-in
        """
        if check_in_time is None:
            check_in_time = datetime.utcnow()

        # Get event details
        event = await self.event_repository.get_by_id(event_id)
        if not event:
            raise ValueError(f"Event {event_id} not found")

        # Check if event has ended
        if check_in_time > event.end_time:
            raise ValueError("Cannot check in after event has ended")

        # Determine if check-in is late
        is_late = event.is_late_checkin(check_in_time)

        return await self.attendance_repository.check_in_user(
            user_id=user_id,
            event_id=event_id,
            check_in_time=check_in_time,
            is_late=is_late
        )

    async def get_user_attendance(
        self,
        user_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Attendance]:
        """Get attendance records for a user."""
        return await self.attendance_repository.list_by_user(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )

    async def get_event_attendance(self, event_id: UUID) -> List[Attendance]:
        """Get all attendance records for an event."""
        return await self.attendance_repository.list_by_event(event_id)

    async def create_initial_attendance_records(self, event_id: UUID) -> List[Attendance]:
        """Create initial attendance records for all users when a new event is synced.

        Args:
            event_id: Event ID

        Returns:
            List of created attendance records with ABSENT status

        Note: This would typically be called when syncing events from Google Calendar
        to ensure all users have attendance records for the event.
        """
        # This would require a UserRepository to get all active users
        # For now, return empty list - will be implemented when user listing is available
        return []

    async def approve_leave_request(
        self,
        user_id: UUID,
        event_id: UUID,
        note: Optional[str] = None
    ) -> Attendance:
        """Approve leave request and update attendance.

        Args:
            user_id: User ID
            event_id: Event ID
            note: Leave reason

        Returns:
            Updated attendance record
        """
        return await self.attendance_repository.mark_as_leave(
            user_id=user_id,
            event_id=event_id,
            note=note
        )

    async def approve_makeup_request(
        self,
        user_id: UUID,
        event_id: UUID,
        note: str
    ) -> Attendance:
        """Approve makeup request and update attendance.

        Args:
            user_id: User ID
            event_id: Event ID
            note: Makeup reason

        Returns:
            Updated attendance record
        """
        return await self.attendance_repository.mark_as_makeup(
            user_id=user_id,
            event_id=event_id,
            note=note
        )

    async def check_in_from_calendar_event(
        self,
        user_id: UUID,
        calendar_event: Dict,
        check_in_time: Optional[datetime] = None
    ) -> Optional[Attendance]:
        """Check in user from Google Calendar event.

        This method handles the M2 milestone core functionality:
        1. Sync Calendar event to Event table (if not exists)
        2. Create attendance record
        3. Determine PRESENT vs LATE status

        Args:
            user_id: User ID to check in
            calendar_event: Google Calendar event data with keys:
                - id: Google Calendar event ID
                - title: Event title
                - description: Event description (optional)
                - start_time: Event start time (ISO 8601 string)
                - end_time: Event end time (ISO 8601 string)
            check_in_time: Check-in time (default: now)

        Returns:
            Attendance record or None if check-in not possible
        """
        from dateutil import parser as date_parser

        if check_in_time is None:
            check_in_time = datetime.utcnow()

        google_event_id = calendar_event.get('id')
        if not google_event_id:
            raise ValueError("Calendar event must have an 'id' field")

        # Parse event times
        try:
            start_time = date_parser.parse(calendar_event['start_time'])
            # Make timezone-aware to UTC if naive
            if start_time.tzinfo is None:
                start_time = start_time.replace(tzinfo=datetime.timezone.utc)

            end_time = date_parser.parse(calendar_event['end_time'])
            if end_time.tzinfo is None:
                end_time = end_time.replace(tzinfo=datetime.timezone.utc)
        except (KeyError, ValueError) as e:
            raise ValueError(f"Invalid event time format: {e}")

        # Check if we're within event time window
        if check_in_time < start_time:
            raise ValueError("Cannot check in before event starts")
        if check_in_time > end_time:
            raise ValueError("Cannot check in after event has ended")

        # Get or create event in our database
        event = await self.event_repository.get_by_google_id(google_event_id)

        if not event:
            # Create new event record
            event = await self.event_repository.create(
                title=calendar_event.get('title', 'Untitled Event'),
                description=calendar_event.get('description'),
                start_time=start_time,
                end_time=end_time,
                google_event_id=google_event_id,
                created_by=None,  # System-synced event
                grace_period_minutes=5  # Default grace period
            )

        # Check if user already checked in for this event
        existing_attendance = await self.attendance_repository.get_by_user_and_event(
            user_id, event.id
        )

        if existing_attendance and existing_attendance.is_present_or_late:
            # Already checked in, return existing record
            return existing_attendance

        # Determine if check-in is late
        is_late = event.is_late_checkin(check_in_time)

        # Create attendance record
        attendance = await self.attendance_repository.check_in_user(
            user_id=user_id,
            event_id=event.id,
            check_in_time=check_in_time,
            is_late=is_late
        )

        return attendance

    async def get_attendance_summary(
        self,
        user_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, int]:
        """Get attendance summary statistics.

        Args:
            user_id: User ID for personal summary (optional)
            start_date: Start date for filtering
            end_date: End date for filtering

        Returns:
            Dictionary with attendance statistics
        """
        # This would require complex aggregation queries
        # For now, return placeholder - will be implemented with proper SQL queries
        return {
            "total_events": 0,
            "present": 0,
            "late": 0,
            "absent": 0,
            "leave": 0,
            "makeup": 0
        }