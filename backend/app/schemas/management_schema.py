from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class RosterEntrySchema(BaseModel):
    user_id: int
    username: str
    role: str
    joined_at: Optional[datetime] = None
    completed_assignments: int = 0
    last_active: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class InviteCodeSchema(BaseModel):
    invite_code: str


class DistributeSchema(BaseModel):
    binder_id: str = Field(..., min_length=1)


class DistributeResultSchema(BaseModel):
    distributed: int
    failed: int = 0
