"""create blog posts

Revision ID: c4d5e6f7a8b9
Revises: b3c4d5e6f7a8
"""

from alembic import op
import sqlalchemy as sa

revision = "c4d5e6f7a8b9"
down_revision = "b3c4d5e6f7a8"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "blog_posts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("week_start", sa.Date(), nullable=False),
        sa.Column("week_end", sa.Date(), nullable=False),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("published_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
        sa.UniqueConstraint("week_start"),
    )
    op.create_index("ix_blog_posts_id", "blog_posts", ["id"])
    op.create_index("ix_blog_posts_slug", "blog_posts", ["slug"])
    op.create_index("ix_blog_posts_week_start", "blog_posts", ["week_start"])


def downgrade():
    op.drop_index("ix_blog_posts_week_start", table_name="blog_posts")
    op.drop_index("ix_blog_posts_slug", table_name="blog_posts")
    op.drop_index("ix_blog_posts_id", table_name="blog_posts")
    op.drop_table("blog_posts")
