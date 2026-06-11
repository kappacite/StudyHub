from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class QuizGenerateRequest(BaseModel):
    note_id: int
    question_count: Optional[int] = Field(7, ge=1, le=20)

class QuizAnswerRequest(BaseModel):
    answer_id: str = Field(..., min_length=1, max_length=1)  # "a", "b", "c", "d"

class QuizCreateFlashcardsRequest(BaseModel):
    deck_id: int
    question_ids: List[int]

class QuizQuestionOptionResponse(BaseModel):
    id: str
    text: str
    correct: bool

class QuizQuestionResponse(BaseModel):
    id: int
    quiz_id: int
    question_text: str
    options: List[QuizQuestionOptionResponse]
    user_answer_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class QuizResponse(BaseModel):
    id: int
    note_id: int
    user_id: int
    score_pct: Optional[float] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    questions: List[QuizQuestionResponse] = []

    model_config = ConfigDict(from_attributes=True)
