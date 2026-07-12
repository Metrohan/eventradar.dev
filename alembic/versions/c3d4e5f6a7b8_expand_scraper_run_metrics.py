"""expand scraper run metrics

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-07-12 00:30:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "c3d4e5f6a7b8"
down_revision = "b2c3d4e5f6a7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for name in ("updated_events", "deactivated_events", "failed_events"):
        op.add_column(
            "scraper_logs",
            sa.Column(name, sa.Integer(), nullable=False, server_default="0"),
        )


def downgrade() -> None:
    for name in ("failed_events", "deactivated_events", "updated_events"):
        op.drop_column("scraper_logs", name)
