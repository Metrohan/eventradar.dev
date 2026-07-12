"""create subscribers table

Revision ID: a9b8c7d6e5f4
Revises: e5f6a7b8c9d0
Create Date: 2026-07-12 14:50:00.000000

The Subscriber model existed in the codebase but relied on
Base.metadata.create_all() at app startup rather than a migration.
That means two different environments disagree about whether this
table already exists:
  - CI's migration-only smoke test (a fresh DB via `alembic upgrade
    head`, no app startup) never had this table, so the next
    migration that ALTERs it failed with "no such table".
  - Production (and any environment that has run the app at least
    once) already has it via create_all(), so unconditionally
    creating it here fails with "relation already exists".
This migration is therefore idempotent: it only creates the table if
it isn't already there.
"""

from alembic import op
import sqlalchemy as sa

revision = "a9b8c7d6e5f4"
down_revision = "e5f6a7b8c9d0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "subscribers" in inspector.get_table_names():
        return

    op.create_table(
        "subscribers",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("contact_info", sa.String(length=255), nullable=False),
        sa.Column("channel", sa.String(length=50), nullable=False),
        sa.Column("interests", sa.JSON(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True, server_default=sa.true()),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
    )


def downgrade() -> None:
    # Tablo bu migration'dan önce de var olabileceğinden (create_all ile)
    # downgrade'de düşürmüyoruz; sonraki migration'ın eklediği kolonları
    # kaldırmak yeterli.
    pass
