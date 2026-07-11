"""add last_seen_at to events

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-07-11 23:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("events", sa.Column("last_seen_at", sa.DateTime(), nullable=True))
    op.execute("UPDATE events SET last_seen_at = scraped_at WHERE last_seen_at IS NULL")
    op.create_index("ix_events_last_seen_at", "events", ["last_seen_at"])


def downgrade() -> None:
    op.drop_index("ix_events_last_seen_at", table_name="events")
    op.drop_column("events", "last_seen_at")
