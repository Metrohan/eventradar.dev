from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class BlogPostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    title: str
    summary: str
    content: str
    week_start: date
    week_end: date
    published_at: datetime


class BlogPostListResponse(BaseModel):
    posts: list[BlogPostResponse]
    total_count: int
