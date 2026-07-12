"""add blog email sent timestamp

Revision ID: d5e6f7a8b9c0
Revises: c4d5e6f7a8b9
"""

from alembic import op
import sqlalchemy as sa

revision = "d5e6f7a8b9c0"
down_revision = "c4d5e6f7a8b9"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "blog_posts", sa.Column("email_sent_at", sa.DateTime(), nullable=True)
    )


def downgrade():
    op.drop_column("blog_posts", "email_sent_at")
