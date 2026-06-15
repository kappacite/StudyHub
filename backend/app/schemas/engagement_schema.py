from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


# ─── Questions des élèves (Q&A) ──────────────────────────────────────────────

class ClassQuestionCreateSchema(BaseModel):
    body: str = Field(..., min_length=1, max_length=2000)


class ClassQuestionAnswerSchema(BaseModel):
    body: str = Field(..., min_length=1, max_length=2000)


class ClassQuestionResponseSchema(BaseModel):
    id: int
    body: str
    answer: Optional[str] = None
    status: str
    author_id: int
    author_username: Optional[str] = None
    answered_by_username: Optional[str] = None
    created_at: datetime
    answered_at: Optional[datetime] = None


# ─── Annonces & fil d'actualité ──────────────────────────────────────────────

class AnnouncementCreateSchema(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    body: Optional[str] = None


class FeedItemSchema(BaseModel):
    id: int
    type: str
    username: str
    payload: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ─── Classement ──────────────────────────────────────────────────────────────

class LeaderboardEntrySchema(BaseModel):
    user_id: int
    username: str
    completed_assignments: int = 0
    avg_score: Optional[float] = None
    streak: int = 0
    points: int = 0
    badges: List[str] = []


class LeaderboardSchema(BaseModel):
    enabled: bool = True
    entries: List[LeaderboardEntrySchema] = []


# ─── Notifications ───────────────────────────────────────────────────────────

class NotificationSchema(BaseModel):
    id: int
    type: str
    title: str
    body: Optional[str] = None
    link: Optional[str] = None
    read: bool = False
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
