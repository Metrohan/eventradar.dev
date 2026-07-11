"""add application_deadline to events

Revision ID: a1b2c3d4e5f6
Revises: ccc17f460dba
Create Date: 2026-07-11 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "ccc17f460dba"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "events",
        sa.Column("application_deadline", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("events", "application_deadline")
