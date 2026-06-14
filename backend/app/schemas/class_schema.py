from datetime import datetime
from typing import Optional, List, Literal, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, model_validator


# Types de tâches supportés par un devoir.
TaskType = Literal["flashcards", "quiz", "exam", "blurting", "read"]


# ─── Input schemas ────────────────────────────────────────────────────────────

class ClassCreateSchema(BaseModel):
    """Créer un groupe de type 'class' (espace de cours)."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    is_public: Optional[bool] = False


class AssignmentTaskCreateSchema(BaseModel):
    """Une tâche d'un devoir. `ref` est l'identifiant public de la cible
    (UUID de classeur/note, ou id numérique) selon le type."""
    task_type: TaskType
    ref: str
    goal: Optional[Dict[str, Any]] = None


class AssignmentCreateSchema(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    instructions: Optional[str] = None
    due_date: Optional[datetime] = None
    publish_at: Optional[datetime] = None
    allow_late: bool = True
    # Voie multi-tâches (préférée)
    tasks: Optional[List[AssignmentTaskCreateSchema]] = None
    # Voie historique mono-classeur (rétro-compatibilité) : synthétise une tâche flashcards.
    binder_id: Optional[str] = None

    @model_validator(mode="after")
    def _require_target(self):
        if not self.tasks and not self.binder_id:
            raise ValueError("Un devoir doit définir au moins une tâche (tasks) ou un binder_id.")
        return self


class TaskSubmitSchema(BaseModel):
    """Soumission d'une tâche par un élève (recalcule la progression depuis le module)."""
    payload: Optional[Dict[str, Any]] = None


# ─── Output schemas ───────────────────────────────────────────────────────────

class AssignmentProgressResponseSchema(BaseModel):
    user_id: int
    username: str
    cards_reviewed: int
    score_pct: Optional[float] = None
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AssignmentTaskResponseSchema(BaseModel):
    id: int
    task_type: str
    ref_id: Optional[int] = None
    ref_uuid: Optional[str] = None
    ref_label: Optional[str] = None
    goal: Optional[Dict[str, Any]] = None
    order: int = 0
    # Progression personnelle (renseignée dans le contexte élève)
    my_status: Optional[str] = None
    my_score_pct: Optional[float] = None
    my_completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AssignmentResponseSchema(BaseModel):
    id: int
    group_id: int
    binder_id: str
    binder_name: str
    title: str
    description: Optional[str] = None
    instructions: Optional[str] = None
    due_date: Optional[datetime] = None
    publish_at: Optional[datetime] = None
    allow_late: bool = True
    created_by: int
    created_at: datetime
    tasks: List[AssignmentTaskResponseSchema] = []
    progress: List[AssignmentProgressResponseSchema] = []

    model_config = ConfigDict(from_attributes=True)


class AssignmentSummarySchema(BaseModel):
    """Version résumée sans la liste de progression (pour la vue élève)."""
    id: int
    group_id: int
    group_name: str
    binder_id: str
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
    tasks: List[AssignmentTaskResponseSchema] = []

    model_config = ConfigDict(from_attributes=True)


class ClassResponseSchema(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    invite_code: str
    type: str
    is_class: bool
    is_public: bool = False
    created_by: Optional[int] = None
    created_at: datetime
    members_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class BinderProgressResponseSchema(BaseModel):
    binder_id: str
    binder_name: str
    cards_reviewed: int
    total_cards: int
    score_pct: float
    last_reviewed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class StudentMaterialsProgressResponseSchema(BaseModel):
    user_id: int
    username: str
    binders_progress: List[BinderProgressResponseSchema] = []

    model_config = ConfigDict(from_attributes=True)
