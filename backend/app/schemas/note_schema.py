from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.tag_schema import TagResponseSchema

class NoteBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = ""
    binder_id: Optional[str] = None

class NoteCreate(NoteBase):
    pass

class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = None
    binder_id: Optional[str] = None
    is_public: Optional[bool] = None

class NoteResponse(NoteBase):
    id: str
    binder_id: Optional[str] = Field(None, validation_alias="binder_uuid")
    user_id: int
    is_public: bool = False
    share_token: Optional[str] = None
    last_blurting_at: Optional[datetime] = None
    tags: List[TagResponseSchema] = []
    created_at: datetime
    updated_at: datetime
    # True quand la note provient d'un classeur partagé (cours) : lecture seule.
    read_only: bool = False
    owner_username: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
