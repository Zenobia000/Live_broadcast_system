"""add google calendar tokens

Revision ID: 2e3f4a5b6c7d
Revises: 1e0b0dc4f480
Create Date: 2025-10-18 15:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2e3f4a5b6c7d'
down_revision: Union[str, None] = '1e0b0dc4f480'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add Google Calendar API token fields to users table
    op.add_column('users', sa.Column('google_refresh_token', sa.Text(), nullable=True, comment='Google OAuth refresh token for Calendar API access'))
    op.add_column('users', sa.Column('google_access_token', sa.Text(), nullable=True, comment='Google OAuth access token (cached, refreshable)'))
    op.add_column('users', sa.Column('google_token_expires_at', sa.DateTime(timezone=True), nullable=True, comment='When the current access token expires'))


def downgrade() -> None:
    # Remove Google Calendar API token fields from users table
    op.drop_column('users', 'google_token_expires_at')
    op.drop_column('users', 'google_access_token')
    op.drop_column('users', 'google_refresh_token')
