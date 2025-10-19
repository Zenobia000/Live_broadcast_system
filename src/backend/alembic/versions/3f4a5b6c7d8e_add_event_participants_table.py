"""add event participants table

Revision ID: 3f4a5b6c7d8e
Revises: 2e3f4a5b6c7d
Create Date: 2025-10-19 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '3f4a5b6c7d8e'
down_revision: Union[str, None] = '2e3f4a5b6c7d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create event_participants table
    op.create_table(
        'event_participants',
        sa.Column('id', sa.Integer(), nullable=False, comment='Primary key'),
        sa.Column('event_id', sa.Integer(), nullable=False, comment='Event ID (CASCADE delete when event is deleted)'),
        sa.Column('user_id', sa.Integer(), nullable=False, comment='User ID (CASCADE delete when user is deleted)'),
        sa.Column('invited_at', sa.DateTime(timezone=True), nullable=False, comment='When the invitation was sent'),
        sa.Column('notification_sent', sa.Boolean(), nullable=False, server_default='false', comment='Whether notification (Email/Slack) was sent'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'), comment='Record creation timestamp'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'), comment='Record last update timestamp'),

        # Primary key
        sa.PrimaryKeyConstraint('id'),

        # Foreign keys
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),

        # Unique constraint (prevent duplicate invitations)
        sa.UniqueConstraint('event_id', 'user_id', name='uq_event_participant'),

        # Table comment
        comment='Event participants and invitation tracking'
    )

    # Create indexes for foreign keys
    op.create_index('ix_event_participants_event_id', 'event_participants', ['event_id'])
    op.create_index('ix_event_participants_user_id', 'event_participants', ['user_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_event_participants_user_id', table_name='event_participants')
    op.drop_index('ix_event_participants_event_id', table_name='event_participants')

    # Drop table
    op.drop_table('event_participants')
