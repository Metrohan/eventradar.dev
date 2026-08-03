"""widen location and path columns to prevent varchar(255) overflow

Revision ID: f7a8b9c0d1e2
Revises: e6f7a8b9c0d1
Create Date: 2026-08-04 00:00:00.000000

events.location and pending_events.location overflow when scrapers pull
full-address strings from new sources.  traffic_logs.path overflows when
bots hit the site with excessively long URLs.  In PostgreSQL, widening
VARCHAR to TEXT (or larger VARCHAR) is a metadata-only operation — no
table rewrite, no locks beyond an ACCESS EXCLUSIVE for the catalog update.
"""

from alembic import op
import sqlalchemy as sa

revision = "f7a8b9c0d1e2"
down_revision = "f1a2b3c4d5e6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "events",
        "location",
        existing_type=sa.String(length=255),
        type_=sa.Text(),
        existing_nullable=True,
    )
    op.alter_column(
        "pending_events",
        "location",
        existing_type=sa.String(length=255),
        type_=sa.Text(),
        existing_nullable=True,
    )
    op.alter_column(
        "traffic_logs",
        "path",
        existing_type=sa.String(length=255),
        type_=sa.String(length=500),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "traffic_logs",
        "path",
        existing_type=sa.String(length=500),
        type_=sa.String(length=255),
        existing_nullable=False,
        postgresql_using="left(path, 255)",
    )
    op.alter_column(
        "pending_events",
        "location",
        existing_type=sa.Text(),
        type_=sa.String(length=255),
        existing_nullable=True,
        postgresql_using="left(location, 255)",
    )
    op.alter_column(
        "events",
        "location",
        existing_type=sa.Text(),
        type_=sa.String(length=255),
        existing_nullable=True,
        postgresql_using="left(location, 255)",
    )
