from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator

class GroupCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None

class GroupJoinSchema(BaseModel):
    invite_code: str = Field(..., min_length=8, max_length=8)

class GroupMemberResponseSchema(BaseModel):
    user_id: int
    username: str
    email: str
    role: str
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)

class GroupBinderResponseSchema(BaseModel):
    group_id: int
    binder_id: str = Field(..., validation_alias="binder_uuid")
    binder_name: str
    permission: str
    pinned: bool
    added_by: Optional[int] = None
    added_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class GroupBinderShareSchema(BaseModel):
    binder_id: str
    permission: str = Field("read", pattern="^(read|write)$")

class GroupActivityResponseSchema(BaseModel):
    id: int
    user_id: int
    username: str
    type: str
    payload: Optional[Any] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class GroupResponseSchema(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    invite_code: str
    created_by: Optional[int] = None
    created_at: datetime
    members_count: int = 0
    binders_count: int = 0

    model_config = ConfigDict(from_attributes=True)

class GroupDetailResponseSchema(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    invite_code: str
    created_by: Optional[int] = None
    created_at: datetime
    members: List[GroupMemberResponseSchema] = []
    binders: List[GroupBinderResponseSchema] = []

    model_config = ConfigDict(from_attributes=True)

class GroupMemberRoleUpdateSchema(BaseModel):
    role: str = Field(..., pattern="^(admin|member)$")

class GroupMemberProgressSchema(BaseModel):
    user_id: int
    username: str
    total_time_seconds: int
    cards_reviewed: int
    cards_correct: int
