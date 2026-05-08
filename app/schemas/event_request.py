from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime, date


class EventRequestBase(BaseModel):
    event_link: HttpUrl
    event_title: str
    event_date: Optional[date] = None
    event_description: Optional[str] = None


class EventRequestCreate(EventRequestBase):
    pass


class EventRequestResponse(EventRequestBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class EventRequestListResponse(BaseModel):
    requests: List[EventRequestResponse]
    total_count: int
