"""Reserve canonical and historical routes in one namespace.

Revision ID: c5d6e7f8a9b0
Revises: b4c5d6e7f8a9
"""

from alembic import op
import sqlalchemy as sa

revision = "c5d6e7f8a9b0"
down_revision = "b4c5d6e7f8a9"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "events",
        sa.Column("slug_version", sa.Integer(), nullable=False, server_default="1"),
    )
    op.create_table(
        "event_slug_aliases",
        sa.Column("slug", sa.String(160), primary_key=True),
        sa.Column(
            "event_id",
            sa.Integer(),
            sa.ForeignKey("events.id", ondelete="CASCADE"),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_event_slug_aliases_event_id", "event_slug_aliases", ["event_id"]
    )
    op.execute(
        "INSERT INTO event_slug_aliases (slug,event_id) SELECT slug,id FROM events"
    )


def downgrade():
    count = (
        op.get_bind()
        .execute(
            sa.text(
                "SELECT count(*) FROM event_slug_aliases a JOIN events e ON e.id=a.event_id WHERE a.slug <> e.slug"
            )
        )
        .scalar()
    )
    if count:
        raise RuntimeError(
            "Historical redirects exist; restore reviewed routes before schema rollback"
        )
    op.drop_index("ix_event_slug_aliases_event_id", table_name="event_slug_aliases")
    op.drop_table("event_slug_aliases")
    op.drop_column("events", "slug_version")
