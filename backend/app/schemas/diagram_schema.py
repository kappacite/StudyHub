from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.tag_schema import TagResponseSchema

class DiagramBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    code: str = ""
    binder_id: Optional[str] = None

class DiagramCreate(DiagramBase):
    pass

class DiagramUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    code: Optional[str] = None
    binder_id: Optional[str] = None

class DiagramResponse(DiagramBase):
    id: int
    binder_id: Optional[str] = Field(None, validation_alias="binder_uuid")
    user_id: int
    tags: List[TagResponseSchema] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
