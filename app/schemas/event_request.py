from pydantic import BaseModel, ConfigDict, HttpUrl
from typing import List, Optional
from datetime import datetime, date


class EventRequestBase(BaseModel):
    event_link: HttpUrl
    event_title: str
    event_date: Optional[date] = None
    event_description: Optional[str] = None
    contact_email: Optional[str] = None


class EventRequestCreate(EventRequestBase):
    pass


class EventRequestResponse(EventRequestBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class EventRequestListResponse(BaseModel):
    requests: List[EventRequestResponse]
    total_count: int
