from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_validator

class StudySessionCreate(BaseModel):
    module: str = Field(..., description="Le module étudié : 'flashcard', 'note', 'diagram'")
    duration_seconds: int = Field(..., ge=0, description="Durée de la session en secondes")
    cards_reviewed: Optional[int] = Field(0, ge=0)
    cards_correct: Optional[int] = Field(0, ge=0)

class StudySessionResponse(StudySessionCreate):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class StatsOverviewResponse(BaseModel):
    streak: int = Field(..., description="Jours consécutifs d'étude")
    total_time_seconds: int = Field(..., description="Temps total d'étude cumulé")
    total_reviewed: int = Field(..., description="Nombre total de flashcards révisées")
    total_correct: int = Field(..., description="Nombre total de flashcards correctes")

class HeatmapItem(BaseModel):
    date: str = Field(..., description="Date au format YYYY-MM-DD")
    duration: int = Field(..., description="Durée cumulée en secondes pour ce jour")
    count: int = Field(..., description="Nombre de sessions pour ce jour")

    @field_validator("date", mode="before")
    @classmethod
    def _coerce_date_to_iso(cls, v):
        # PostgreSQL renvoie un datetime.date pour func.date() (SQLite une str).
        # On normalise en "YYYY-MM-DD" pour éviter un 400 de validation en prod.
        return v.isoformat() if hasattr(v, "isoformat") else v

class DeckStatsResponse(BaseModel):
    deck_id: int
    retention_rate: float = Field(..., description="Taux de réussite aux révisions (pourcentage)")
    next_review: Optional[datetime] = None
    cards_to_review: int = Field(..., description="Nombre de cartes prêtes pour révision")
    total_cards: int = Field(..., description="Nombre total de cartes dans le deck")

class DashboardKpis(BaseModel):
    total_cards_studied: int
    mature_cards: int
    retention_rate: float

class DashboardStatsResponse(BaseModel):
    kpi: DashboardKpis
    heatmap: dict[str, int]
    maturity_distribution: dict[str, int]
    forecast_7_days: dict[str, int]
