from sqlalchemy import Boolean, Column, Date, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from ..core.database import Base


class BlogPost(Base):
    __tablename__ = "blog_posts"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    title = Column(String(300), nullable=False)
    summary = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    week_start = Column(Date, nullable=False, unique=True, index=True)
    week_end = Column(Date, nullable=False)
    is_published = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    published_at = Column(DateTime, default=func.now(), nullable=False)
    email_sent_at = Column(DateTime, nullable=True)
