"""
Google Calendar API service for event synchronization.

Design Philosophy:
- Clean abstraction over Google Calendar API
- Event synchronization with local database
- Robust error handling for API failures
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.core.config import settings
from app.models.calendar.event import Event


class GoogleCalendarService:
    """Google Calendar API service."""

    def __init__(self, credentials: Optional[Credentials] = None):
        """Initialize Google Calendar service.

        Args:
            credentials: Google OAuth credentials for API access
        """
        self.credentials = credentials
        self.service = None
        if credentials:
            self.service = build('calendar', 'v3', credentials=credentials)

    async def list_events(
        self,
        calendar_id: str = 'primary',
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None,
        max_results: int = 50
    ) -> List[Dict]:
        """List events from Google Calendar.

        Args:
            calendar_id: Google Calendar ID (default: 'primary')
            time_min: Lower bound for event start times
            time_max: Upper bound for event start times
            max_results: Maximum number of events to return

        Returns:
            List of event dictionaries from Google Calendar API

        Raises:
            Exception: If Calendar API call fails
        """
        if not self.service:
            raise ValueError("Calendar service not initialized with credentials")

        try:
            # Set default time range if not provided
            if time_min is None:
                time_min = datetime.utcnow()
            if time_max is None:
                time_max = time_min + timedelta(days=30)

            # Format times for Google API (RFC3339)
            time_min_str = time_min.isoformat() + 'Z'
            time_max_str = time_max.isoformat() + 'Z'

            # Call Google Calendar API
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min_str,
                timeMax=time_max_str,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])

            # Filter events that have start/end times (not all-day events)
            filtered_events = []
            for event in events:
                start = event['start'].get('dateTime')
                end = event['end'].get('dateTime')

                if start and end:  # Only events with specific times
                    filtered_events.append({
                        'id': event['id'],
                        'title': event['summary'],
                        'description': event.get('description'),
                        'start_time': start,
                        'end_time': end,
                        'creator': event.get('creator', {})
                    })

            return filtered_events

        except HttpError as error:
            raise Exception(f"Google Calendar API error: {error}")

    async def get_event(self, event_id: str, calendar_id: str = 'primary') -> Optional[Dict]:
        """Get specific event from Google Calendar.

        Args:
            event_id: Google Calendar event ID
            calendar_id: Google Calendar ID (default: 'primary')

        Returns:
            Event dictionary or None if not found

        Raises:
            Exception: If Calendar API call fails
        """
        if not self.service:
            raise ValueError("Calendar service not initialized with credentials")

        try:
            event = self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()

            # Return formatted event data
            start = event['start'].get('dateTime')
            end = event['end'].get('dateTime')

            if not start or not end:
                return None  # Skip all-day events

            return {
                'id': event['id'],
                'title': event['summary'],
                'description': event.get('description'),
                'start_time': start,
                'end_time': end,
                'creator': event.get('creator', {})
            }

        except HttpError as error:
            if error.resp.status == 404:
                return None  # Event not found
            raise Exception(f"Google Calendar API error: {error}")

    def parse_datetime(self, datetime_str: str) -> datetime:
        """Parse Google Calendar datetime string.

        Args:
            datetime_str: RFC3339 datetime string from Google Calendar

        Returns:
            Parsed datetime object in UTC
        """
        from dateutil import parser
        return parser.parse(datetime_str).replace(tzinfo=None)

    async def sync_events_to_database(
        self,
        calendar_events: List[Dict],
        event_repository
    ) -> List[Event]:
        """Sync Google Calendar events to local database.

        Args:
            calendar_events: Events from Google Calendar API
            event_repository: Event repository for database operations

        Returns:
            List of created/updated Event objects

        Raises:
            Exception: If database sync fails
        """
        synced_events = []

        for calendar_event in calendar_events:
            try:
                # Check if event already exists
                existing_event = await event_repository.get_by_google_id(
                    calendar_event['id']
                )

                if existing_event:
                    # Update existing event
                    existing_event.title = calendar_event['title']
                    existing_event.description = calendar_event.get('description')
                    existing_event.start_time = self.parse_datetime(calendar_event['start_time'])
                    existing_event.end_time = self.parse_datetime(calendar_event['end_time'])

                    updated_event = await event_repository.update(existing_event)
                    synced_events.append(updated_event)
                else:
                    # Create new event
                    new_event = await event_repository.create(
                        title=calendar_event['title'],
                        description=calendar_event.get('description'),
                        start_time=self.parse_datetime(calendar_event['start_time']),
                        end_time=self.parse_datetime(calendar_event['end_time']),
                        google_event_id=calendar_event['id'],
                        created_by=None  # System-synced events have no creator
                    )
                    synced_events.append(new_event)

            except Exception as e:
                # Log error but continue with other events
                print(f"Failed to sync event {calendar_event['id']}: {str(e)}")
                continue

        return synced_events