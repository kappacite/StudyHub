from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class NoteBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = ""
    binder_id: Optional[int] = None

class NoteCreate(NoteBase):
    pass

class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = None
    binder_id: Optional[int] = None
    is_public: Optional[bool] = None

from app.schemas.flashcard_schema import FlashcardResponse

class NoteResponse(NoteBase):
    id: int
    user_id: int
    is_public: bool = False
    share_token: Optional[str] = None
    flashcards: List[FlashcardResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
