"""Distinguish automatic deactivation from manual/unknown hides.

Revision ID: a2b3c4d5e6f7
Revises: f7a8b9c0d1e2
"""

from alembic import op
import sqlalchemy as sa

revision = "a2b3c4d5e6f7"
down_revision = "f7a8b9c0d1e2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # NULL preserves ambiguous legacy inactive rows; never infer manual intent.
    op.add_column(
        "events", sa.Column("deactivation_reason", sa.String(16), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("events", "deactivation_reason")
