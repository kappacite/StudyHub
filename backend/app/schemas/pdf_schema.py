from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class PDFBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    binder_id: Optional[int] = None

class PDFCreate(PDFBase):
    pass

class PDFResponse(PDFBase):
    id: int
    filename: str
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
