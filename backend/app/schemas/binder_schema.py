from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class BinderBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    parent_id: Optional[int] = None

class BinderCreate(BinderBase):
    pass

class BinderUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    parent_id: Optional[int] = None

class BinderResponse(BinderBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
