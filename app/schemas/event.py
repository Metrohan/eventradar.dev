from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    date: Optional[datetime] = None
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
    location: Optional[str] = None
    url: Optional[str] = None
    image_url: Optional[str] = None
    source: Optional[str] = None
    is_active: Optional[bool] = None

class EventResponse(EventBase):
    id: int
    scraped_at: datetime
    
    class Config:
        from_attributes = True

class EventListResponse(BaseModel):
    events: list[EventResponse]
    total_count: int
    last_updated: Optional[str] = None


