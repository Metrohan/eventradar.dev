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
    inspector = sa.inspect(op.get_bind())
    if not inspector.has_table("scraper_logs"):
        op.create_table(
            "scraper_logs",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("source", sa.String(length=100), nullable=False),
            sa.Column("status", sa.String(length=50), nullable=False),
            sa.Column("events_found", sa.Integer(), nullable=True),
            sa.Column("new_events", sa.Integer(), nullable=True),
            sa.Column(
                "updated_events", sa.Integer(), nullable=False, server_default="0"
            ),
            sa.Column(
                "deactivated_events", sa.Integer(), nullable=False, server_default="0"
            ),
            sa.Column(
                "failed_events", sa.Integer(), nullable=False, server_default="0"
            ),
            sa.Column("error_message", sa.Text(), nullable=True),
            sa.Column("duration_seconds", sa.Float(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.func.now(),
            ),
        )
        op.create_index("ix_scraper_logs_id", "scraper_logs", ["id"])
        return

    for name in ("updated_events", "deactivated_events", "failed_events"):
        op.add_column(
            "scraper_logs",
            sa.Column(name, sa.Integer(), nullable=False, server_default="0"),
        )


def downgrade() -> None:
    for name in ("failed_events", "deactivated_events", "updated_events"):
        op.drop_column("scraper_logs", name)
