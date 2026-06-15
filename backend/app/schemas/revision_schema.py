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


# --- Statistiques (A7 / D5) --------------------------------------------------

class RevisionHistoryPoint(BaseModel):
    date: datetime
    grade: Optional[int] = None


class RevisionItemStats(BaseModel):
    item_id: int
    reviews: int
    success_rate: float          # % grade >= 3 sur l'historique
    lapses: int                  # nb d'échecs (grade < 3)
    repetitions: int
    ease_factor: float
    interval: int
    next_review: Optional[datetime] = None
    last_reviewed: Optional[datetime] = None
    # Indicateurs DSR/FSRS dérivés (cf. D5).
    stability_days: int          # S ≈ intervalle
    difficulty: float            # D ∈ [1,10] dérivée de l'ease factor
    retrievability: float        # R ∈ [0,1] (courbe d'oubli d'Ebbinghaus)
    is_mature: bool              # intervalle ≥ seuil de maturité
    is_leech: bool               # échoué de façon répétée (sangsue)
    mastered: bool
    mastery_date: Optional[datetime] = None  # date de maîtrise estimée (projection SM-2)
    history: List[RevisionHistoryPoint] = []


class RevisionItemSummary(BaseModel):
    item_id: int
    label: str
    reviews: int
    success_rate: float
    difficulty: float
    retrievability: float
    is_leech: bool
    is_mature: bool
    due: bool


class RevisionSetStats(BaseModel):
    set_id: int
    type: str
    name: str
    items_count: int
    reviewed_items: int
    mastered_count: int
    mastery_rate: float          # % d'items mûrs
    avg_success_rate: float
    true_retention: float        # % grade≥3 sur les items mûrs (True Retention)
    leeches_count: int
    due_count: int               # items à réviser maintenant
    avg_difficulty: float
    verdicts: List[str] = []     # messages actionnables
    items: List[RevisionItemSummary] = []
