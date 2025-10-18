"""
Google OAuth 2.0 service for authentication.

Design Philosophy:
- Single responsibility: handle OAuth flow only
- Clean interface for OAuth operations
- Secure token handling
"""

import logging
import secrets
from typing import Dict, Optional

import httpx
from authlib.integrations.starlette_client import OAuth
from starlette.applications import Starlette

from app.core.config import settings

logger = logging.getLogger(__name__)


class GoogleOAuthService:
    """Google OAuth 2.0 service."""

    def __init__(self):
        self.oauth = OAuth()

        # Build scopes: basic auth + calendar access
        scopes = [
            'openid',
            'email',
            'profile',
            'https://www.googleapis.com/auth/calendar.readonly',
            'https://www.googleapis.com/auth/calendar.events.readonly'
        ]

        self.oauth.register(
            name='google',
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={
                'scope': ' '.join(scopes),
                'prompt': 'select_account',
                'access_type': 'offline',  # Request refresh token for long-term calendar access
            }
        )

    async def get_authorization_url(self, request) -> tuple[str, str]:
        """Generate OAuth authorization URL.

        Args:
            request: Starlette request object

        Returns:
            Tuple of (authorization_url, state)
        """
        # Generate state manually
        state = secrets.token_urlsafe(32)

        # Save state in session
        request.session['oauth_state'] = state

        redirect_uri = settings.GOOGLE_REDIRECT_URI
        result = await self.oauth.google.create_authorization_url(
            redirect_uri,
            state=state  # Pass our state explicitly
        )

        # Debug logging
        logger.info(f"[OAuth] Generated authorization URL")
        logger.info(f"[OAuth] State generated: {state}")
        logger.info(f"[OAuth] State saved in session: {request.session.get('oauth_state')}")
        logger.info(f"[OAuth] Session keys: {list(request.session.keys())}")

        return result['url'], state

    async def exchange_code_for_token(self, request, code: str, state: str) -> Dict:
        """Exchange authorization code for access token.

        Args:
            request: Starlette request object
            code: Authorization code from Google
            state: State parameter for CSRF protection

        Returns:
            User info dictionary with Google profile data

        Raises:
            Exception: If token exchange fails
        """
        redirect_uri = settings.GOOGLE_REDIRECT_URI

        # Debug logging
        logger.info(f"[OAuth] Callback received")
        logger.info(f"[OAuth] State from URL: {state}")
        logger.info(f"[OAuth] Session keys: {list(request.session.keys())}")
        logger.info(f"[OAuth] State from session: {request.session.get('oauth_state', 'NO_STATE')}")

        # Verify state manually
        session_state = request.session.get('oauth_state')
        if not session_state or session_state != state:
            logger.error(f"[OAuth] State mismatch! Session: {session_state}, URL: {state}")
            raise Exception(f"mismatching_state: CSRF Warning! State not equal in request and response.")

        # Clear state from session
        request.session.pop('oauth_state', None)

        logger.info(f"[OAuth] State verified successfully")

        try:
            # Exchange code for token using Google's token endpoint directly
            logger.info(f"[OAuth] Exchanging code for token...")

            async with httpx.AsyncClient() as client:
                token_response = await client.post(
                    'https://oauth2.googleapis.com/token',
                    data={
                        'code': code,
                        'client_id': settings.GOOGLE_CLIENT_ID,
                        'client_secret': settings.GOOGLE_CLIENT_SECRET,
                        'redirect_uri': redirect_uri,
                        'grant_type': 'authorization_code',
                    }
                )
                token_response.raise_for_status()
                token = token_response.json()

            logger.info(f"[OAuth] Token exchange successful")

            # Fetch user info from Google API
            logger.info(f"[OAuth] Fetching user info from Google API...")
            user_info = await self._fetch_user_info(token['access_token'])
            logger.info(f"[OAuth] User info retrieved: {user_info.get('email')}")
            logger.info(f"[OAuth] User info keys: {list(user_info.keys())}")

            # Google OAuth2 v2 uses 'id' instead of 'sub'
            google_id = user_info.get('sub') or user_info.get('id')

            return {
                'google_id': google_id,
                'email': user_info['email'],
                'name': user_info['name'],
                'avatar_url': user_info.get('picture'),
                'access_token': token['access_token'],
                'refresh_token': token.get('refresh_token'),  # For Calendar API long-term access
                'id_token': token.get('id_token'),
                'expires_in': token.get('expires_in', 3600),
            }

        except Exception as e:
            logger.error(f"[OAuth] Token exchange failed: {str(e)}", exc_info=True)
            raise Exception(f"OAuth token exchange failed: {str(e)}")

    async def _fetch_user_info(self, access_token: str) -> Dict:
        """Fetch user info from Google API using access token."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            response.raise_for_status()
            return response.json()

    async def verify_token(self, id_token: str) -> Optional[Dict]:
        """Verify Google ID token.

        Args:
            id_token: Google ID token to verify

        Returns:
            Decoded token payload or None if invalid
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f'https://oauth2.googleapis.com/tokeninfo?id_token={id_token}'
                )

                if response.status_code != 200:
                    return None

                token_info = response.json()

                # Verify audience matches our client ID
                if token_info.get('aud') != settings.GOOGLE_CLIENT_ID:
                    return None

                return token_info

        except Exception:
            return None