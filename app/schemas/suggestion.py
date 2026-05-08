from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class SuggestionBase(BaseModel):
    suggestion_type: str
    suggestion_title: str
    suggestion_text: str


class SuggestionCreate(SuggestionBase):
    pass


class SuggestionResponse(SuggestionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class SuggestionListResponse(BaseModel):
    suggestions: List[SuggestionResponse]
    total_count: int
