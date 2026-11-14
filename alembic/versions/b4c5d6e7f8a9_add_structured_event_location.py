"""add structured location fields to events

Revision ID: b4c5d6e7f8a9
Revises: a3b4c5d6e7f8
Create Date: 2026-11-14 00:00:00.000000

Adds nullable city / attendance / venue columns, derived from the free-text
location by the Event model (see app.utils.location). The columns are not
backfilled here so the migration does not depend on application code: every
scrape assigns ``location`` again and refreshes the fields of the rows it
touches. Adding nullable columns is a metadata-only change.
"""

from alembic import op
import sqlalchemy as sa

revision = "b4c5d6e7f8a9"
down_revision = "a3b4c5d6e7f8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("events", sa.Column("city", sa.String(length=64), nullable=True))
    op.add_column(
        "events", sa.Column("attendance", sa.String(length=16), nullable=True)
    )
    op.add_column("events", sa.Column("venue", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("events", "venue")
    op.drop_column("events", "attendance")
    op.drop_column("events", "city")
