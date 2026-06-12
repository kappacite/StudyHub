from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.tag_schema import TagResponseSchema

class PDFBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    binder_id: Optional[str] = None

class PDFCreate(PDFBase):
    pass

class PDFResponse(PDFBase):
    id: str
    binder_id: Optional[str] = Field(None, validation_alias="binder_uuid")
    filename: str
    user_id: int
    tags: List[TagResponseSchema] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
