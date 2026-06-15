from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

# D3c : une flashcard est strictement recto/verso. Les types interactifs (QCM,
# vrai/faux, association, définition, ordre) sont portés par RevisionSet/RevisionItem,
# pas par les decks/flashcards.

class FlashcardBase(BaseModel):
    front: str = Field(..., min_length=1)
    back: str = Field(..., min_length=1)

class FlashcardCreate(FlashcardBase):
    tuning: float = Field(1.0, gt=0)

class FlashcardUpdate(BaseModel):
    front: Optional[str] = Field(None, min_length=1)
    back: Optional[str] = Field(None, min_length=1)
    tuning: Optional[float] = Field(None, gt=0)

class FlashcardAnswer(BaseModel):
    score: int = Field(..., ge=0, le=5, description="Score d'évaluation SM-2 de 0 à 5")

class FlashcardHistoryEntry(BaseModel):
    date: datetime
    grade: Optional[int] = None

class FlashcardResponse(FlashcardBase):
    id: int
    deck_id: int
    tuning: float = 1.0
    reverse_of_id: Optional[int] = None
    placeholder_hash: Optional[str] = None
    original_text: Optional[str] = None
    ease_factor: float
    interval: int
    repetitions: int
    next_review: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
