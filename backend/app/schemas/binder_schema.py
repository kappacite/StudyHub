from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class BinderBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    parent_id: Optional[int] = None
    is_public: Optional[bool] = False
    description: Optional[str] = None
    tags: Optional[List[str]] = None

class BinderCreate(BinderBase):
    pass

class BinderUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    parent_id: Optional[int] = None
    is_public: Optional[bool] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None

class BinderResponse(BinderBase):
    id: int
    user_id: int
    fork_count: int
    original_author_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
