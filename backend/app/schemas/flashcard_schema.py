from datetime import datetime
from typing import Optional, Literal, Any, Dict
from pydantic import BaseModel, Field, ConfigDict

CardType = Literal["basic", "qcm", "vf", "ordre", "assoc"]

class FlashcardBase(BaseModel):
    front: str = Field(..., min_length=1)
    back: str = Field(..., min_length=1)

class FlashcardCreate(FlashcardBase):
    # 'basic' = recto/verso ; types interactifs portent leur contenu dans payload.
    card_type: CardType = "basic"
    payload: Optional[Dict[str, Any]] = None

class FlashcardUpdate(BaseModel):
    front: Optional[str] = Field(None, min_length=1)
    back: Optional[str] = Field(None, min_length=1)
    card_type: Optional[CardType] = None
    payload: Optional[Dict[str, Any]] = None

class FlashcardAnswer(BaseModel):
    score: int = Field(..., ge=0, le=5, description="Score d'évaluation SM-2 de 0 à 5")

class FlashcardResponse(FlashcardBase):
    id: int
    deck_id: int
    card_type: str = "basic"
    payload: Optional[Dict[str, Any]] = None
    placeholder_hash: Optional[str] = None
    original_text: Optional[str] = None
    ease_factor: float
    interval: int
    repetitions: int
    next_review: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
