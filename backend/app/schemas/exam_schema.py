from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict, model_validator

class ExamStartRequest(BaseModel):
    binder_id: str
    duration_minutes: Optional[int] = Field(30, ge=15, le=120)
    include_flashcards: Optional[bool] = True
    include_qcm: Optional[bool] = True
    question_limit: Optional[int] = Field(20, ge=5, le=50)

class ExamAnswerRequest(BaseModel):
    answer: Any

class ExamItemOptionResponse(BaseModel):
    id: str
    text: str
    correct: Optional[bool] = None

class ExamItemResponse(BaseModel):
    id: int
    item_type: str
    item_id: int
    front: str
    back: Optional[str] = None
    options: Optional[List[ExamItemOptionResponse]] = None
    user_answer: Optional[Any] = None
    is_correct: Optional[bool] = None

class ExamResponse(BaseModel):
    id: int
    binder_id: Optional[str] = Field(None, validation_alias="binder_uuid")
    user_id: int
    duration_seconds: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    score_pct: Optional[float] = None
    flashcard_score: Optional[float] = None
    qcm_score: Optional[float] = None
    time_taken_seconds: Optional[int] = None
    items: List[ExamItemResponse] = Field(..., validation_alias="items_snapshot")

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="after")
    def hide_answers(self) -> 'ExamResponse':
        if self.completed_at is None:
            # L'examen est en cours : masquer les réponses de QCM
            for item in self.items:
                if item.options:
                    for opt in item.options:
                        opt.correct = None
        return self
