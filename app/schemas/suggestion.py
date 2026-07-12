from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime


class SuggestionBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    suggestion_type: str = Field(min_length=2, max_length=50)
    suggestion_title: str = Field(min_length=3, max_length=200)
    suggestion_text: str = Field(min_length=10, max_length=5000)


class SuggestionCreate(SuggestionBase):
    pass


class SuggestionResponse(SuggestionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class SuggestionListResponse(BaseModel):
    suggestions: List[SuggestionResponse]
    total_count: int
