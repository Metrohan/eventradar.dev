"""expand traffic log user agent

Revision ID: e6f7a8b9c0d1
Revises: d5e6f7a8b9c0
"""

from alembic import op
import sqlalchemy as sa


revision = "e6f7a8b9c0d1"
down_revision = "d5e6f7a8b9c0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "traffic_logs" not in inspector.get_table_names():
        op.create_table(
            "traffic_logs",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("path", sa.String(length=255), nullable=False),
            sa.Column("method", sa.String(length=10), nullable=False),
            sa.Column("ip_address", sa.String(length=45), nullable=True),
            sa.Column("user_agent", sa.Text(), nullable=True),
            sa.Column("timestamp", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_traffic_logs_id"), "traffic_logs", ["id"])
        return

    op.alter_column(
        "traffic_logs",
        "user_agent",
        existing_type=sa.String(length=255),
        type_=sa.Text(),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "traffic_logs",
        "user_agent",
        existing_type=sa.Text(),
        type_=sa.String(length=255),
        existing_nullable=True,
        postgresql_using="left(user_agent, 255)",
    )
