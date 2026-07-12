"""add subscriber confirm/unsubscribe tokens and push_subscriptions table

Revision ID: b3c4d5e6f7a8
Revises: e5f6a7b8c9d0
Create Date: 2026-07-12 15:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "b3c4d5e6f7a8"
down_revision = "a9b8c7d6e5f4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "subscribers",
        sa.Column("confirmed", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "subscribers", sa.Column("confirm_token", sa.String(length=64), nullable=True)
    )
    op.add_column(
        "subscribers",
        sa.Column("unsubscribe_token", sa.String(length=64), nullable=True),
    )
    op.create_index(
        "ix_subscribers_confirm_token", "subscribers", ["confirm_token"], unique=True
    )
    op.create_index(
        "ix_subscribers_unsubscribe_token",
        "subscribers",
        ["unsubscribe_token"],
        unique=True,
    )

    op.create_table(
        "push_subscriptions",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("endpoint", sa.String(length=1000), nullable=False, unique=True),
        sa.Column("p256dh", sa.String(length=255), nullable=False),
        sa.Column("auth", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("push_subscriptions")
    op.drop_index("ix_subscribers_unsubscribe_token", table_name="subscribers")
    op.drop_index("ix_subscribers_confirm_token", table_name="subscribers")
    op.drop_column("subscribers", "unsubscribe_token")
    op.drop_column("subscribers", "confirm_token")
    op.drop_column("subscribers", "confirmed")
