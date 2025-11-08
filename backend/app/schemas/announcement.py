from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AnnouncementBase(BaseModel):
    title: str
    message: str

class AnnouncementCreate(AnnouncementBase):
    pass

class AnnouncementResponse(AnnouncementBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class AnnouncementListResponse(BaseModel):
    announcements: list[AnnouncementResponse]
    total_count: int


