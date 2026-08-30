from datetime import date, datetime
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
    # Optionnel (D8, bibliotheque-ensembles) : absent/None = ensemble
    # heterogene (le type vit au niveau de l'item, cf. RevisionItemCreate.type).
    type: RevisionType | None = None
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
    # Duree reelle ecoulee sur cet item (Task 9) -- optionnelle pour retro-
    # compatibilite avec un client qui ne l'envoie pas encore : defaut 0,
    # jamais estime/invente.
    duration_seconds: int = Field(0, ge=0)


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


# --- QCM par question (check/commit — A2/D6, Task 2 revision-flexibilite) ---
# Remplace l'ancien passage scoré en lot (RevisionRunRequest/RevisionRunResult) :
# meme principe de scission check/commit que RevisionCheckRequest/RevisionGradeRequest
# (Task 1), applique question par question plutot qu'en un seul lot.


class RevisionQcmAnswerRequest(BaseModel):
    selected_option_ids: list[str] = []


class RevisionQcmCommitRequest(BaseModel):
    selected_option_ids: list[str] = []
    # Note SM-2 (1-5) choisie par l'utilisateur apres avoir vu la correction
    # (cf. RevisionQcmCheckResult) -- requise, jamais deduite cote serveur.
    score: int = Field(..., ge=1, le=5)
    # Duree reelle ecoulee sur CETTE question -- optionnelle, defaut 0, jamais
    # estimee/inventee. Remplace la repartition divmod du lot (Task 9) : chaque
    # question a desormais sa propre duree mesuree cote frontend.
    duration_seconds: int = Field(0, ge=0)


class RevisionQcmCheckResult(BaseModel):
    correct: bool
    earned: int
    points: int
    correct_option_ids: list[str]


class RevisionQcmAnswerResult(RevisionQcmCheckResult):
    item: RevisionItemResponse


# --- Correction d'un item à l'étude (A3/A4/A6 : vf, association, ordre) -------


class RevisionCheckRequest(BaseModel):
    # Réponse spécifique au type :
    #   vf          -> {"value": bool}
    #   association -> {"matches": {left: right}}
    #   ordre       -> {"order": [str, ...]}
    answer: dict[str, Any]


class RevisionCheckResult(BaseModel):
    correct: bool


class RevisionGradeRequest(BaseModel):
    # Réponse spécifique au type :
    #   vf          -> {"value": bool}
    #   association -> {"matches": {left: right}}
    #   ordre       -> {"order": [str, ...]}
    answer: dict[str, Any]
    # Note SM-2 (1-5) choisie par l'utilisateur après avoir vu la correction
    # (scission check/grade, Task 1 revision-flexibilite) -- requise, jamais
    # déduite côté serveur.
    score: int = Field(..., ge=1, le=5)
    # Duree reelle ecoulee sur cet item (Task 9) -- optionnelle, defaut 0.
    duration_seconds: int = Field(0, ge=0)


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
    type: str
    label: str
    reviews: int
    success_rate: float
    difficulty: float
    retrievability: float
    is_leech: bool
    is_mature: bool
    due: bool


class GradeDistribution(BaseModel):
    """Répartition des notes SM-2 (0-5) en 4 paliers pédagogiques : 0-1 -> Encore
    (échec net), 2 -> Difficile (échec limité), 3-4 -> Bien (réussite avec effort),
    5 -> Facile (réussite parfaite). Le seuil réussite/échec de SM-2 lui-même
    (score >= 3, cf. invariants-sm2) tombe pile entre « hard » et « good » -- ce
    bucketing ajoute une graduation de chaque côté de cette frontière, il ne la
    déplace pas."""

    again: int = 0
    hard: int = 0
    good: int = 0
    easy: int = 0


class WeeklyProgressionPoint(BaseModel):
    """Un point de la fenêtre des 6 dernières semaines (index 0 = plus ancienne,
    index 5 = semaine courante), semaines ISO lundi-dimanche."""

    reviews: int = 0
    success_rate: float = 0.0


class SessionHistoryDay(BaseModel):
    """Une ligne d'historique = un jour calendaire (created_at.date()) agrégeant
    toutes les sessions notées de l'ensemble ce jour-là."""

    date: date
    reviews: int
    success_rate: float
    duration_seconds: int = 0


class RevisionSetStats(BaseModel):
    set_id: int
    type: str | None = None
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
    # Stats de la page RevisionSetStats (D9/reviser-hub-redesign) : calculées à
    # partir des sessions déjà chargées par get_set_stats, aucune requête de plus.
    grade_distribution: GradeDistribution = GradeDistribution()
    weekly_progression: list[WeeklyProgressionPoint] = []
    session_history: list[SessionHistoryDay] = []
    # Temps cumule reel (Task 9), somme des StudySession deja chargees.
    total_duration_seconds: int = 0


# --- Stats par classeur (A8) -------------------------------------------------


class RevisionSetSummary(BaseModel):
    """Résumé d'un ensemble dans la vue agrégée d'un classeur (sans les items)."""

    set_id: int
    type: str | None = None
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
    # UUID publics du classeur + de son sous-arbre effectivement inclus (selon
    # include_descendants) -- permet au frontend de scoper d'autres ressources
    # (ex. decks) sur le même périmètre sans re-marcher l'arbre des classeurs
    # (cf. revue de branche reviser-hub, finding #3).
    binder_ids: list[str] = []
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
    # Temps total d'etude reel (Task 9), somme des sessions de tous les
    # ensembles de revision du classeur -- les decks de flashcards ne sont
    # pas inclus (duree non trackee cote flashcard_service, hors perimetre).
    total_duration_seconds: int = 0
