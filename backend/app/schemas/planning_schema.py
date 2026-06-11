from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class DeckBreakdownSchema(BaseModel):
    deck_id: int
    deck_name: str
    count: int

    model_config = ConfigDict(from_attributes=True)

class PlanningDaySchema(BaseModel):
    date: str  # YYYY-MM-DD
    total_due: int
    breakdown: List[DeckBreakdownSchema]

    model_config = ConfigDict(from_attributes=True)

class PlanningCalendarResponse(BaseModel):
    days: List[PlanningDaySchema]

class PlanningAdvanceRequest(BaseModel):
    deck_id: int
    card_ids: Optional[List[int]] = None
    date: Optional[str] = None
