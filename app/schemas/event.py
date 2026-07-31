from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import List, Optional
from datetime import datetime


class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    date: Optional[datetime] = None
    application_deadline: Optional[datetime] = None
    location: Optional[str] = None
    url: str
    image_url: Optional[str] = None
    source: str = "Admin"
    is_active: bool = True


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[datetime] = None
    application_deadline: Optional[datetime] = None
    location: Optional[str] = None
    url: Optional[str] = None
    image_url: Optional[str] = None
    source: Optional[str] = None
    is_active: Optional[bool] = None


class EventResponse(EventBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    scraped_at: datetime
    thumbnail_url: Optional[str] = None
    tags: list[str] = Field(default_factory=list)

    @field_validator("tags", mode="before")
    @classmethod
    def extract_tag_names(cls, v):
        if not v:
            return []
        return [t.name if hasattr(t, "name") else t for t in v]


class EventListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    events: List[EventResponse]
    total_count: int
    last_updated: Optional[str] = None
    page: int = 1
    page_size: int = 100
    total_pages: int = 0
