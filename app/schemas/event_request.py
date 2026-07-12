from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl
from typing import List, Optional
from datetime import datetime, date


class EventRequestBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    event_link: HttpUrl
    event_title: str = Field(min_length=3, max_length=500)
    event_date: Optional[date] = None
    event_description: Optional[str] = Field(default=None, max_length=5000)
    contact_email: Optional[EmailStr] = None


class EventRequestCreate(EventRequestBase):
    pass


class EventRequestResponse(EventRequestBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class EventRequestListResponse(BaseModel):
    requests: List[EventRequestResponse]
    total_count: int
