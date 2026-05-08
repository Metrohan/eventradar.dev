from pydantic import BaseModel
from typing import Any, List, Optional
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
    announcements: List[AnnouncementResponse]
    total_count: int

    class Config:
        from_attributes = True
