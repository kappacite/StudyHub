from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class DiagramBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    code: str = ""
    binder_id: Optional[int] = None

class DiagramCreate(DiagramBase):
    pass

class DiagramUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    code: Optional[str] = None
    binder_id: Optional[int] = None

class DiagramResponse(DiagramBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
