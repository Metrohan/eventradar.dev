"""Add immutable unique event slugs; backfill legacy rows without loading app code."""

from alembic import op
import sqlalchemy as sa

revision = "a3b4c5d6e7f8"
down_revision = "a2b3c4d5e6f7"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("events", sa.Column("slug", sa.String(160), nullable=True))
    op.execute(
        sa.text(
            "UPDATE events SET slug = 'etkinlik-' || CAST(id AS VARCHAR) WHERE slug IS NULL"
        )
    )
    dialect = op.get_bind().dialect.name
    # Database default keeps old application/scraper writers and app-only rollback
    # compatible. PostgreSQL >=13 includes gen_random_uuid() without an extension.
    default = (
        "('etkinlik-' || replace(CAST(gen_random_uuid() AS TEXT), '-', ''))"
        if dialect == "postgresql"
        else "('etkinlik-' || lower(hex(randomblob(16))))"
    )
    with op.batch_alter_table("events") as batch:
        batch.alter_column(
            "slug",
            existing_type=sa.String(160),
            nullable=False,
            server_default=sa.text(default),
        )
        batch.create_unique_constraint("uq_events_slug", ["slug"])


def downgrade():
    with op.batch_alter_table("events") as batch:
        batch.drop_constraint("uq_events_slug", type_="unique")
        batch.drop_column("slug")
