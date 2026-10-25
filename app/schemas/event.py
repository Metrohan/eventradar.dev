from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import List, Optional
from datetime import datetime
from urllib.parse import urlparse
from ..utils.event_dates import local_datetime


class EventValidation(BaseModel):
    @field_validator("title", "source", check_fields=False)
    @classmethod
    def required_text(cls, value):
        if value is None or not value.strip():
            raise ValueError("Must not be blank")
        return value.strip()

    @field_validator("url", "image_url", check_fields=False)
    @classmethod
    def http_url(cls, value, info):
        if info.field_name == "image_url" and not value:
            return None
        if not value:
            raise ValueError("URL is required")
        parsed = urlparse(value)
        if (
            parsed.scheme not in ("http", "https")
            or not parsed.hostname
            or parsed.username
            or parsed.password
            or any(char.isspace() for char in value)
        ):
            raise ValueError("Must be an HTTP(S) URL without credentials")
        return value

    @field_validator("date", "application_deadline", mode="before", check_fields=False)
    @classmethod
    def blank_date(cls, value):
        return None if value == "" else value

    @field_validator("date", "application_deadline", check_fields=False)
    @classmethod
    def local_date(cls, value):
        return local_datetime(value) if value else value


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


class EventCreate(EventValidation, EventBase):
    title: str = Field(min_length=1, max_length=500)
    url: str = Field(max_length=500)
    image_url: Optional[str] = Field(default=None, max_length=500)
    source: str = Field(default="Admin", min_length=1, max_length=100)


class EventUpdate(EventValidation):
    title: Optional[str] = Field(default=None, min_length=1, max_length=500)
    description: Optional[str] = None
    date: Optional[datetime] = None
    application_deadline: Optional[datetime] = None
    location: Optional[str] = None
    url: Optional[str] = Field(default=None, max_length=500)
    image_url: Optional[str] = Field(default=None, max_length=500)
    source: Optional[str] = Field(default=None, min_length=1, max_length=100)
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
