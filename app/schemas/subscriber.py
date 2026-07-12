from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import List, Optional
from datetime import datetime


class SubscriberBase(BaseModel):
    contact_info: str
    channel: str  # 'telegram', 'email'
    interests: List[str] = Field(default_factory=list)
    is_active: bool = True


class SubscriberCreate(SubscriberBase):
    pass


class SubscriberResponse(SubscriberBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class BroadcastRequest(BaseModel):
    message: str = Field(min_length=10, max_length=4096)
    target_channel: str = "all"  # 'all', 'telegram', 'email'
    target_interest: Optional[str] = None  # Filter by tag


class EmailSubscribeRequest(BaseModel):
    email: EmailStr


class PushSubscribeRequest(BaseModel):
    endpoint: str = Field(min_length=1, max_length=1000)
    keys: dict[str, str]  # {"p256dh": "...", "auth": "..."}
