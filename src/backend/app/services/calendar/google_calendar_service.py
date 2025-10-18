"""
Google Calendar API service for event synchronization.

Design Philosophy:
- Clean abstraction over Google Calendar API with automatic token refresh
- Integration with User model for token management
- Event synchronization with local database
- Robust error handling for API failures
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.auth.user import User
from app.models.calendar.event import Event

logger = logging.getLogger(__name__)


class GoogleCalendarService:
    """Google Calendar API service with automatic token management."""

    def __init__(self, user: User, db_session: AsyncSession):
        """Initialize Google Calendar service for a specific user.

        Args:
            user: User model with Google OAuth tokens
            db_session: Database session for token updates
        """
        self.user = user
        self.db_session = db_session
        self.base_url = "https://www.googleapis.com/calendar/v3"

    async def _get_valid_access_token(self) -> str:
        """Get a valid access token, refreshing if necessary.

        Returns:
            Valid Google OAuth access token

        Raises:
            Exception: If token refresh fails or user has no refresh token
        """
        # Check if access token is still valid
        if self.user.google_access_token and self.user.google_token_expires_at:
            if datetime.utcnow() < self.user.google_token_expires_at - timedelta(minutes=5):
                # Token is valid for at least 5 more minutes
                return self.user.google_access_token

        # Need to refresh token
        if not self.user.google_refresh_token:
            raise Exception("User has no refresh token - must re-authenticate with Calendar scopes")

        logger.info(f"[Calendar] Refreshing access token for user {self.user.email}")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                'https://oauth2.googleapis.com/token',
                data={
                    'client_id': settings.GOOGLE_CLIENT_ID,
                    'client_secret': settings.GOOGLE_CLIENT_SECRET,
                    'refresh_token': self.user.google_refresh_token,
                    'grant_type': 'refresh_token',
                }
            )

            if response.status_code != 200:
                logger.error(f"[Calendar] Token refresh failed: {response.text}")
                raise Exception(f"Token refresh failed: {response.text}")

            token_data = response.json()

            # Update user's access token
            self.user.google_access_token = token_data['access_token']
            self.user.google_token_expires_at = datetime.utcnow() + timedelta(
                seconds=token_data.get('expires_in', 3600)
            )

            # Persist to database
            await self.db_session.commit()
            await self.db_session.refresh(self.user)

            logger.info(f"[Calendar] Token refreshed successfully for user {self.user.email}")

            return self.user.google_access_token

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
        access_token = await self._get_valid_access_token()

        try:
            # Set default time range if not provided
            if time_min is None:
                time_min = datetime.utcnow()
            if time_max is None:
                time_max = time_min + timedelta(days=30)

            # Format times for Google API (RFC3339)
            time_min_str = time_min.isoformat() + 'Z'
            time_max_str = time_max.isoformat() + 'Z'

            # Call Google Calendar API using httpx
            params = {
                'timeMin': time_min_str,
                'timeMax': time_max_str,
                'maxResults': max_results,
                'singleEvents': True,
                'orderBy': 'startTime',
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/calendars/{calendar_id}/events",
                    headers={'Authorization': f'Bearer {access_token}'},
                    params=params
                )
                response.raise_for_status()
                data = response.json()

            events = data.get('items', [])

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

            logger.info(f"[Calendar] Retrieved {len(filtered_events)} events for user {self.user.email}")
            return filtered_events

        except httpx.HTTPStatusError as error:
            logger.error(f"[Calendar] API error: {error.response.text}")
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
        access_token = await self._get_valid_access_token()

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/calendars/{calendar_id}/events/{event_id}",
                    headers={'Authorization': f'Bearer {access_token}'}
                )
                response.raise_for_status()
                event = response.json()

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

        except httpx.HTTPStatusError as error:
            if error.response.status_code == 404:
                return None  # Event not found
            logger.error(f"[Calendar] Get event error: {error.response.text}")
            raise Exception(f"Google Calendar API error: {error}")

    async def check_if_user_in_event_now(self) -> Optional[Dict]:
        """Check if user should be in an event right now.

        This checks if there's a calendar event happening at the current time
        that the user should attend (for automatic check-in).

        Returns:
            Current event dict if user should be in an event, None otherwise
        """
        now = datetime.utcnow()

        # Get events from 1 hour ago to 1 hour in the future
        # (to catch events that started recently)
        time_min = now - timedelta(hours=1)
        time_max = now + timedelta(hours=1)

        events = await self.list_events(
            time_min=time_min,
            time_max=time_max,
            max_results=10
        )

        # Check which event the user should be in right now
        for event in events:
            start_time = self.parse_datetime(event['start_time'])
            end_time = self.parse_datetime(event['end_time'])

            if start_time and end_time:
                if start_time <= now <= end_time:
                    logger.info(f"[Calendar] User {self.user.email} should be in event: {event.get('title')}")
                    return event

        return None

    async def get_upcoming_events_for_today(self) -> List[Dict]:
        """Get upcoming events for today (from now until end of day).

        This is a convenience method for attendance checking.

        Returns:
            List of events happening today
        """
        now = datetime.utcnow()
        end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        return await self.list_events(
            time_min=now,
            time_max=end_of_day,
            order_by='startTime'
        )

    def parse_datetime(self, datetime_str: str) -> Optional[datetime]:
        """Parse Google Calendar datetime string.

        Args:
            datetime_str: RFC3339 datetime string from Google Calendar

        Returns:
            Parsed datetime object in UTC or None if parsing fails
        """
        if not datetime_str:
            return None

        try:
            # Remove 'Z' suffix and parse
            if datetime_str.endswith('Z'):
                datetime_str = datetime_str[:-1] + '+00:00'

            # Try parsing with timezone, then convert to naive UTC
            from dateutil import parser
            return parser.parse(datetime_str).replace(tzinfo=None)
        except Exception as e:
            logger.error(f"[Calendar] Failed to parse datetime '{datetime_str}': {e}")
            return None

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