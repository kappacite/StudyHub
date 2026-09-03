from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


class NoteGradeResponse(BaseModel):
    score: int
    verdict: str
    points_forts: List[str]
    ameliorations: List[str]
    suggestions: Optional[str] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
