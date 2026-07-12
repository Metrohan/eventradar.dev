from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


class SuggestionBase(BaseModel):
    suggestion_type: str
    suggestion_title: str
    suggestion_text: str


class SuggestionCreate(SuggestionBase):
    pass


class SuggestionResponse(SuggestionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class SuggestionListResponse(BaseModel):
    suggestions: List[SuggestionResponse]
    total_count: int
