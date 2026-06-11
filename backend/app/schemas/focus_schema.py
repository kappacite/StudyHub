from pydantic import BaseModel
from typing import List, Optional

class FocusItemSchema(BaseModel):
    type: str  # "deck" | "note"
    id: int
    title: str
    count: int
    is_late: bool
    last_session_ago_days: Optional[int] = None

    class Config:
        from_attributes = True

class FocusTodayResponse(BaseModel):
    total_due: int
    late_count: int
    flashcard_count: int
    blurting_count: int
    items: List[FocusItemSchema]

    class Config:
        from_attributes = True

class ForecastItemSchema(BaseModel):
    date: str  # "YYYY-MM-DD"
    count: int
    load_level: str  # "low" | "medium" | "high"

    class Config:
        from_attributes = True

class FocusForecastResponse(BaseModel):
    forecast: List[ForecastItemSchema]

    class Config:
        from_attributes = True

class RetentionSubjectSchema(BaseModel):
    binder_id: int
    binder_name: str
    retention_pct: float
    overdue_count: int
    trend_7d: float

    class Config:
        from_attributes = True

class FocusRetentionResponse(BaseModel):
    by_subject: List[RetentionSubjectSchema]

    class Config:
        from_attributes = True
