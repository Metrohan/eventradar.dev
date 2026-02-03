from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ScraperLogBase(BaseModel):
    source: str
    status: str
    events_found: int = 0
    new_events: int = 0
    error_message: Optional[str] = None
    duration_seconds: float = 0.0

class ScraperLogCreate(ScraperLogBase):
    pass

class ScraperLogResponse(ScraperLogBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
