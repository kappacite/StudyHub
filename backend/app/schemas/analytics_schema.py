from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class AssignmentStatSchema(BaseModel):
    id: int
    title: str
    due_date: Optional[datetime] = None
    submissions_count: int = 0
    completed_count: int = 0
    completion_rate: float = 0.0   # 0..100
    avg_score: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class ClassOverviewSchema(BaseModel):
    class_id: int
    students_count: int
    assignments_count: int
    completion_rate: float = 0.0       # 0..100, sur l'ensemble des soumissions
    avg_score: Optional[float] = None
    active_students_7d: int = 0
    assignments: List[AssignmentStatSchema] = []


class WeakTopicSchema(BaseModel):
    note_id: int
    note_title: str
    error_rate: float                  # 0..100
    sample: int                        # nb d'items évalués (taille d'échantillon)


class ClassInsightSchema(BaseModel):
    class_id: int
    weak_topics: List[WeakTopicSchema] = []
    summary: str = ""
    ai: bool = False
    created_at: Optional[datetime] = None
