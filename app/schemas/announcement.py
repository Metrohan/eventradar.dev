from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


class AnnouncementBase(BaseModel):
    title: str
    message: str


class AnnouncementCreate(AnnouncementBase):
    pass


class AnnouncementResponse(AnnouncementBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class AnnouncementListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    announcements: List[AnnouncementResponse]
    total_count: int
