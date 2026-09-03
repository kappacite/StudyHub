from pydantic import BaseModel, ConfigDict
from typing import List, Literal, Optional

class BreakdownItemSchema(BaseModel):
    # notes-ia-planning-corrections, Task 1 : generalise l'ancien DeckBreakdownSchema
    # (deck_id/deck_name) pour couvrir aussi les RevisionSet -- kind discrimine la
    # source cote frontend (routage du bouton "Reviser").
    kind: Literal["deck", "revision_set"]
    id: int
    name: str
    count: int

    model_config = ConfigDict(from_attributes=True)

class PlanningDaySchema(BaseModel):
    date: str  # YYYY-MM-DD
    total_due: int
    breakdown: List[BreakdownItemSchema]

    model_config = ConfigDict(from_attributes=True)

class PlanningCalendarResponse(BaseModel):
    days: List[PlanningDaySchema]

class PlanningAdvanceRequest(BaseModel):
    deck_id: Optional[int] = None
    set_id: Optional[int] = None
    card_ids: Optional[List[int]] = None
    date: Optional[str] = None
