from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class ScraperLogBase(BaseModel):
    source: str
    status: str
    events_found: int = 0
    new_events: int = 0
    updated_events: int = 0
    deactivated_events: int = 0
    failed_events: int = 0
    attempts: int = 1
    error_message: Optional[str] = None
    duration_seconds: float = 0.0


class ScraperLogCreate(ScraperLogBase):
    pass


class ScraperLogResponse(ScraperLogBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
