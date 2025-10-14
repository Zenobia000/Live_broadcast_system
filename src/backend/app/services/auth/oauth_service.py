"""
Google OAuth 2.0 service for authentication.

Design Philosophy:
- Single responsibility: handle OAuth flow only
- Clean interface for OAuth operations
- Secure token handling
"""

from typing import Dict, Optional

import httpx
from authlib.integrations.starlette_client import OAuth
from starlette.applications import Starlette

from app.core.config import settings


class GoogleOAuthService:
    """Google OAuth 2.0 service."""

    def __init__(self):
        self.oauth = OAuth()
        self.oauth.register(
            name='google',
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={
                'scope': 'openid email profile',
                'prompt': 'select_account',
            }
        )

    def get_authorization_url(self, request) -> tuple[str, str]:
        """Generate OAuth authorization URL.

        Args:
            request: Starlette request object

        Returns:
            Tuple of (authorization_url, state)
        """
        redirect_uri = settings.GOOGLE_REDIRECT_URI
        return self.oauth.google.create_authorization_url(
            request, redirect_uri
        )

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

        try:
            # Exchange code for token
            token = await self.oauth.google.authorize_access_token(
                request, redirect_uri=redirect_uri
            )

            # Parse the ID token to get user info
            user_info = token.get('userinfo')
            if not user_info:
                # Fallback: fetch user info from Google API
                user_info = await self._fetch_user_info(token['access_token'])

            return {
                'google_id': user_info['sub'],
                'email': user_info['email'],
                'name': user_info['name'],
                'avatar_url': user_info.get('picture'),
                'access_token': token['access_token'],
                'id_token': token.get('id_token'),
            }

        except Exception as e:
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