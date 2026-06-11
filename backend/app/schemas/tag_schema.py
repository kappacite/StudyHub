from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class TagCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=30)
    color: Optional[str] = Field(None, max_length=7)


class TagUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=30)
    color: Optional[str] = Field(None, max_length=7)


class TagSetSchema(BaseModel):
    tag_ids: List[int] = []


class TagResponseSchema(BaseModel):
    id: int
    name: str
    color: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TagListResponseSchema(BaseModel):
    data: List[TagResponseSchema]
