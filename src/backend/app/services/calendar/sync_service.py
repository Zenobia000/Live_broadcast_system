"""
Calendar synchronization service.

Design Philosophy:
- Scheduled sync with Google Calendar
- Automatic attendance record creation
- Robust error handling for API failures
"""

from datetime import datetime, timedelta
from typing import Dict, List
from uuid import UUID

from google.oauth2.credentials import Credentials

from app.models.calendar.event import Event
from app.models.enums import AttendanceStatus
from app.repositories.attendance.attendance_repository import AttendanceRepository
from app.repositories.auth.user_repository import UserRepository
from app.services.calendar.calendar_service import CalendarService


class SyncService:
    """Service for calendar synchronization and attendance initialization."""

    def __init__(
        self,
        calendar_service: CalendarService,
        attendance_repository: AttendanceRepository,
        user_repository: UserRepository
    ):
        self.calendar_service = calendar_service
        self.attendance_repository = attendance_repository
        self.user_repository = user_repository

    async def sync_calendar_events(
        self,
        credentials: Credentials,
        calendar_id: str = 'primary',
        days_ahead: int = 30
    ) -> Dict:
        """Sync events from Google Calendar and create attendance records.

        Args:
            credentials: Google OAuth credentials
            calendar_id: Google Calendar ID
            days_ahead: Number of days to sync ahead

        Returns:
            Sync results summary
        """
        results = {
            "events_synced": 0,
            "events_created": 0,
            "events_updated": 0,
            "attendance_records_created": 0,
            "errors": []
        }

        try:
            # Sync events from Google Calendar
            synced_events = await self.calendar_service.sync_events_from_google(
                credentials=credentials,
                calendar_id=calendar_id,
                days_ahead=days_ahead
            )

            results["events_synced"] = len(synced_events)

            # Create initial attendance records for new events
            for event in synced_events:
                try:
                    attendance_count = await self.create_attendance_records_for_event(event.id)
                    results["attendance_records_created"] += attendance_count
                except Exception as e:
                    results["errors"].append(f"Failed to create attendance for event {event.id}: {str(e)}")

        except Exception as e:
            results["errors"].append(f"Calendar sync failed: {str(e)}")

        return results

    async def create_attendance_records_for_event(self, event_id: UUID) -> int:
        """Create initial attendance records for all users for a new event.

        Args:
            event_id: Event ID

        Returns:
            Number of attendance records created

        Note: This creates ABSENT records for all users, which will be updated
        when users check in or when leave/makeup requests are approved.
        """
        # TODO: This requires getting all active users
        # For now, return 0 - will implement when user listing is available
        # The logic would be:
        # 1. Get all active users
        # 2. For each user, create ABSENT attendance record
        # 3. Return count of created records
        return 0

    async def sync_upcoming_events(
        self,
        credentials: Credentials,
        hours_ahead: int = 24
    ) -> List[Event]:
        """Sync upcoming events and prepare attendance tracking.

        Args:
            credentials: Google OAuth credentials
            hours_ahead: Hours to look ahead for events

        Returns:
            List of upcoming events
        """
        # Get upcoming events from local database
        upcoming_events = await self.calendar_service.list_upcoming_events(
            hours_ahead=hours_ahead
        )

        # Sync any missing events from Google Calendar
        sync_results = await self.sync_calendar_events(
            credentials=credentials,
            days_ahead=hours_ahead // 24 + 1  # Convert hours to days
        )

        return upcoming_events

    async def get_sync_status(self) -> Dict:
        """Get calendar synchronization status.

        Returns:
            Sync status information
        """
        # Get recent events to determine last sync
        current_time = datetime.utcnow()
        recent_events = await self.calendar_service.get_events_in_range(
            start_time=current_time - timedelta(days=1),
            end_time=current_time + timedelta(days=1)
        )

        return {
            "last_sync_estimated": current_time.isoformat() if recent_events else None,
            "events_in_next_24h": len([
                e for e in recent_events
                if e.start_time >= current_time
            ]),
            "ongoing_events": len([
                e for e in recent_events
                if e.start_time <= current_time <= e.end_time
            ]),
            "sync_health": "healthy" if recent_events else "no_recent_events"
        }