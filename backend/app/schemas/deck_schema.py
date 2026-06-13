from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.tag_schema import TagResponseSchema

class DeckBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    binder_id: Optional[str] = None

class DeckCreate(DeckBase):
    pass

class DeckUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    binder_id: Optional[str] = None

class DeckResponse(DeckBase):
    id: int
    binder_id: Optional[str] = Field(None, validation_alias="binder_uuid")
    user_id: int
    # Injecté par le service (COUNT groupé) ; 0 par défaut si non fourni.
    card_count: int = 0
    tags: List[TagResponseSchema] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
