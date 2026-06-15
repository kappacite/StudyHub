from datetime import datetime
from typing import Optional, Literal, Any, Dict, List
from pydantic import BaseModel, Field, ConfigDict

# Types d'ensembles génériques (cf. app.models.revision.REVISION_SET_TYPES).
RevisionType = Literal["qcm", "vf", "association", "definition", "ordre"]


# --- Ensembles ---------------------------------------------------------------

class RevisionSetCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: RevisionType
    description: Optional[str] = None
    binder_id: Optional[str] = None
    tuning_default: float = Field(1.0, gt=0)


class RevisionSetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    binder_id: Optional[str] = None
    tuning_default: Optional[float] = Field(None, gt=0)


class RevisionSetResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    type: str
    binder_id: Optional[str] = Field(None, validation_alias="binder_uuid")
    user_id: int
    tuning_default: float
    is_public: bool
    # Injecté par le service (COUNT groupé) ; 0 par défaut si non fourni.
    item_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Items -------------------------------------------------------------------

class RevisionItemCreate(BaseModel):
    payload: Dict[str, Any]
    tuning: float = Field(1.0, gt=0)
    position: int = 0


class RevisionItemUpdate(BaseModel):
    payload: Optional[Dict[str, Any]] = None
    tuning: Optional[float] = Field(None, gt=0)
    position: Optional[int] = None


class RevisionItemAnswer(BaseModel):
    score: int = Field(..., ge=0, le=5, description="Score d'évaluation SM-2 de 0 à 5")


class RevisionItemResponse(BaseModel):
    id: int
    set_id: int
    payload: Dict[str, Any]
    tuning: float
    position: int
    ease_factor: float
    interval: int
    repetitions: int
    next_review: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Passage scoré (QCM — A2/D6) --------------------------------------------

class RevisionRunAnswer(BaseModel):
    item_id: int
    selected_option_ids: List[str] = []


class RevisionRunRequest(BaseModel):
    answers: List[RevisionRunAnswer]


class RevisionRunQuestionResult(BaseModel):
    item_id: int
    correct: bool
    earned: int
    points: int
    correct_option_ids: List[str]
    selected_option_ids: List[str]


class RevisionRunResult(BaseModel):
    score: int
    max_score: int
    percentage: float
    results: List[RevisionRunQuestionResult]


# --- Correction d'un item à l'étude (A3/A4/A6 : vf, association, ordre) -------

class RevisionGradeRequest(BaseModel):
    # Réponse spécifique au type :
    #   vf          -> {"value": bool}
    #   association -> {"matches": {left: right}}
    #   ordre       -> {"order": [str, ...]}
    answer: Dict[str, Any]


class RevisionGradeResult(BaseModel):
    correct: bool
    item: RevisionItemResponse
