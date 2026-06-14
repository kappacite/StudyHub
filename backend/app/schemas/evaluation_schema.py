from datetime import datetime
from typing import Optional, List, Any, Dict, Literal
from pydantic import BaseModel, Field, ConfigDict


# --- Requêtes ---

class EvaluationGenerateRequest(BaseModel):
    note_id: str
    item_count: int = Field(8, ge=4, le=20)
    force: bool = False  # forcer une nouvelle génération IA même si le cache est valide


class EvaluationAnswerRequest(BaseModel):
    # value : id d'option (qcm), booléen (vf), texte (trou/open)
    value: Any = None
    # auto-évaluation des items ouverts uniquement
    self_grade: Optional[Literal["acquired", "partial", "missed"]] = None


class EvaluationFlashcardsRequest(BaseModel):
    """Ajout opt-in de flashcards (items ratés) à un deck réel choisi par l'élève."""
    deck_id: int
    item_ids: List[int] = Field(default_factory=list, min_length=1)


# --- Réponses ---

class EvaluationItemResponse(BaseModel):
    id: int
    type: str
    source: str
    # payload SANITISÉ pour la vue question (sans clé de correction), ou révélé
    # quand l'évaluation est complétée.
    payload: Dict[str, Any]
    user_answer: Optional[Dict[str, Any]] = None
    is_correct: Optional[bool] = None


class ProposedCard(BaseModel):
    """Carte de révision PROPOSÉE (non créée) pour un item raté. L'élève décide
    s'il l'ajoute à un deck."""
    item_id: int
    front: str
    back: str


class EvaluationResponse(BaseModel):
    id: int
    note_id: str
    user_id: int
    score_pct: Optional[float] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    items: List[EvaluationItemResponse] = []
    # Renseigné à la complétion : suggestions de cartes pour les items ratés.
    proposed_cards: List[ProposedCard] = []

    model_config = ConfigDict(from_attributes=True)


class FlashcardsCreatedResponse(BaseModel):
    created: int


class EvaluationAnswerResponse(BaseModel):
    item_id: int
    is_correct: Optional[bool] = None
    # correction révélée pour CET item (bonne option, réponse, réponse-modèle...)
    correction: Dict[str, Any] = {}
