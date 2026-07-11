from pydantic import BaseModel, field_validator
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
    id: int
    scraped_at: datetime
    tags: list[str] = []

    @field_validator("tags", mode="before")
    @classmethod
    def extract_tag_names(cls, v):
        if not v:
            return []
        return [t.name if hasattr(t, "name") else t for t in v]

    class Config:
        from_attributes = True


class EventListResponse(BaseModel):
    events: List[EventResponse]
    total_count: int
    last_updated: Optional[str] = None

    class Config:
        from_attributes = True
