from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime


class SubscriberBase(BaseModel):
    contact_info: str
    channel: str  # 'telegram', 'email'
    interests: List[str] = []
    is_active: bool = True


class SubscriberCreate(SubscriberBase):
    pass


class SubscriberResponse(SubscriberBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class BroadcastRequest(BaseModel):
    message: str = Field(min_length=10, max_length=4096)
    target_channel: str = "all"  # 'all', 'telegram', 'email'
    target_interest: Optional[str] = None  # Filter by tag
