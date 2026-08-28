from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

# Types d'ensembles génériques (cf. app.models.revision.REVISION_SET_TYPES).
RevisionType = Literal["qcm", "vf", "association", "definition", "ordre"]
# Types d'items (D8) : les 5 types d'ensemble + flashcard (item-only, ne
# peut pas etre le type homogene d'un RevisionSet, cf. RevisionType).
RevisionItemType = Literal["qcm", "vf", "association", "definition", "ordre", "flashcard"]


# --- Ensembles ---------------------------------------------------------------


class RevisionSetCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: RevisionType
    description: str | None = None
    binder_id: str | None = None
    tuning_default: float = Field(1.0, gt=0)


class RevisionSetUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    binder_id: str | None = None
    tuning_default: float | None = Field(None, gt=0)


class RevisionSetResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    # Optionnel (D8) : None = ensemble heterogene (type porte par les items).
    # Aucun code actuel ne produit encore None -- tous les ensembles reels
    # restent homogenes et renseignes.
    type: str | None = None
    binder_id: str | None = Field(None, validation_alias="binder_uuid")
    user_id: int
    tuning_default: float
    is_public: bool
    # Injecté par le service (COUNT groupé) ; 0 par défaut si non fourni.
    item_count: int = 0
    # Vrai quand l'ensemble provient d'un classeur partagé (cours) : l'utilisateur
    # peut l'étudier mais pas l'éditer.
    read_only: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Items -------------------------------------------------------------------


class RevisionItemCreate(BaseModel):
    # Optionnel : si absent, retombe sur le type de l'ensemble parent
    # (retro-compatibilite totale avec le frontend actuel, qui n'envoie
    # jamais ce champ).
    type: RevisionItemType | None = None
    payload: dict[str, Any]
    tuning: float = Field(1.0, gt=0)
    position: int = 0


class RevisionItemUpdate(BaseModel):
    payload: dict[str, Any] | None = None
    tuning: float | None = Field(None, gt=0)
    position: int | None = None


class RevisionItemAnswer(BaseModel):
    score: int = Field(..., ge=0, le=5, description="Score d'évaluation SM-2 de 0 à 5")


class RevisionItemResponse(BaseModel):
    id: int
    set_id: int
    # Optionnel : reflete la colonne DB (nullable par prudence, cf. Task 1).
    # Garanti renseigne en pratique par le service (Task 3) des que
    # create_item/update_item cablent le type explicitement.
    type: str | None = None
    payload: dict[str, Any]
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
    selected_option_ids: list[str] = []


class RevisionRunRequest(BaseModel):
    answers: list[RevisionRunAnswer]


class RevisionRunQuestionResult(BaseModel):
    item_id: int
    correct: bool
    earned: int
    points: int
    correct_option_ids: list[str]
    selected_option_ids: list[str]


class RevisionRunResult(BaseModel):
    score: int
    max_score: int
    percentage: float
    results: list[RevisionRunQuestionResult]


# --- Correction d'un item à l'étude (A3/A4/A6 : vf, association, ordre) -------


class RevisionGradeRequest(BaseModel):
    # Réponse spécifique au type :
    #   vf          -> {"value": bool}
    #   association -> {"matches": {left: right}}
    #   ordre       -> {"order": [str, ...]}
    answer: dict[str, Any]


class RevisionGradeResult(BaseModel):
    correct: bool
    item: RevisionItemResponse


# --- Statistiques (A7 / D5) --------------------------------------------------


class RevisionHistoryPoint(BaseModel):
    date: datetime
    grade: int | None = None


class RevisionItemStats(BaseModel):
    item_id: int
    reviews: int
    success_rate: float  # % grade >= 3 sur l'historique
    lapses: int  # nb d'échecs (grade < 3)
    repetitions: int
    ease_factor: float
    interval: int
    next_review: datetime | None = None
    last_reviewed: datetime | None = None
    # Indicateurs DSR/FSRS dérivés (cf. D5).
    stability_days: int  # S ≈ intervalle
    difficulty: float  # D ∈ [1,10] dérivée de l'ease factor
    retrievability: float  # R ∈ [0,1] (courbe d'oubli d'Ebbinghaus)
    is_mature: bool  # intervalle ≥ seuil de maturité
    is_leech: bool  # échoué de façon répétée (sangsue)
    mastered: bool
    mastery_date: datetime | None = None  # date de maîtrise estimée (projection SM-2)
    history: list[RevisionHistoryPoint] = []


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
    mastery_rate: float  # % d'items mûrs
    avg_success_rate: float
    true_retention: float  # % grade≥3 sur les items mûrs (True Retention)
    leeches_count: int
    due_count: int  # items à réviser maintenant
    avg_difficulty: float
    verdicts: list[str] = []  # messages actionnables
    items: list[RevisionItemSummary] = []


# --- Stats par classeur (A8) -------------------------------------------------


class RevisionSetSummary(BaseModel):
    """Résumé d'un ensemble dans la vue agrégée d'un classeur (sans les items)."""

    set_id: int
    type: str
    name: str
    items_count: int
    reviewed_items: int
    mastered_count: int
    mastery_rate: float
    avg_success_rate: float
    true_retention: float
    leeches_count: int
    due_count: int
    avg_difficulty: float


class RevisionTypeBreakdown(BaseModel):
    """Répartition par type d'ensemble dans un classeur."""

    type: str
    sets_count: int
    items_count: int
    mastered_count: int
    mastery_rate: float


class RevisionBinderStats(BaseModel):
    binder_id: str  # UUID public du classeur
    name: str
    include_descendants: bool = True
    sets_count: int
    items_count: int
    reviewed_items: int
    mastered_count: int
    mastery_rate: float
    avg_success_rate: float
    true_retention: float
    leeches_count: int
    due_count: int
    avg_difficulty: float
    by_type: list[RevisionTypeBreakdown] = []
    sets: list[RevisionSetSummary] = []
    weakest_sets: list[RevisionSetSummary] = []  # ensembles les plus à risque
    verdicts: list[str] = []
