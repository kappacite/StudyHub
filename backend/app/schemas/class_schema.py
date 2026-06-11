from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


# ─── Input schemas ────────────────────────────────────────────────────────────

class ClassCreateSchema(BaseModel):
    """Créer un groupe de type 'class' (espace de cours)."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class AssignmentCreateSchema(BaseModel):
    binder_id: int
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    due_date: Optional[datetime] = None


# ─── Output schemas ───────────────────────────────────────────────────────────

class AssignmentProgressResponseSchema(BaseModel):
    user_id: int
    username: str
    cards_reviewed: int
    score_pct: Optional[float] = None
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AssignmentResponseSchema(BaseModel):
    id: int
    group_id: int
    binder_id: int
    binder_name: str
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    created_by: int
    created_at: datetime
    progress: List[AssignmentProgressResponseSchema] = []

    model_config = ConfigDict(from_attributes=True)


class AssignmentSummarySchema(BaseModel):
    """Version résumée sans la liste de progression (pour la vue élève)."""
    id: int
    group_id: int
    group_name: str
    binder_id: int
    binder_name: str
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    created_at: datetime
    # Progression personnelle
    my_cards_reviewed: int = 0
    my_score_pct: Optional[float] = None
    my_completed_at: Optional[datetime] = None
    status: str = "todo"   # "todo" | "in_progress" | "done" | "late"

    model_config = ConfigDict(from_attributes=True)


class ClassResponseSchema(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    invite_code: str
    type: str
    is_class: bool
    created_by: Optional[int] = None
    created_at: datetime
    members_count: int = 0

    model_config = ConfigDict(from_attributes=True)
