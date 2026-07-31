"""add thumbnail_url to events

Revision ID: f1a2b3c4d5e6
Revises: e6f7a8b9c0d1
"""

from alembic import op
import sqlalchemy as sa

revision = "f1a2b3c4d5e6"
down_revision = "e6f7a8b9c0d1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "events", sa.Column("thumbnail_url", sa.String(length=500), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("events", "thumbnail_url")
