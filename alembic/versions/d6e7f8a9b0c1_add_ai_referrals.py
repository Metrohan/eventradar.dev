"""count page views that an AI assistant sent

Revision ID: d6e7f8a9b0c1
Revises: c5d6e7f8a9b0
Create Date: 2026-11-15 00:00:00.000000

One row per such page view: a label from a fixed list, the landing path and a
time. No IP, user agent or referrer URL. Rows older than the traffic-log
retention are purged with it.
"""

from alembic import op
import sqlalchemy as sa

revision = "d6e7f8a9b0c1"
down_revision = "c5d6e7f8a9b0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_referrals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source", sa.String(32), nullable=False),
        sa.Column("path", sa.String(255), nullable=False),
        sa.Column(
            "timestamp", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_ai_referrals_timestamp", "ai_referrals", ["timestamp"])


def downgrade() -> None:
    op.drop_index("ix_ai_referrals_timestamp", table_name="ai_referrals")
    op.drop_table("ai_referrals")
