from datetime import datetime
from typing import Optional, List, Literal, Union
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.tag_schema import TagResponseSchema

class BinderBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    parent_id: Optional[str] = None
    is_public: Optional[bool] = False
    description: Optional[str] = None

class BinderCreate(BinderBase):
    tags: Optional[List[str]] = None

class BinderUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    parent_id: Optional[str] = None
    is_public: Optional[bool] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None

class BinderItemRef(BaseModel):
    """Référence à un élément rattachable (C1)."""
    type: Literal["note", "deck", "set", "diagram", "pdf"]
    id: Union[int, str]

class BinderItemsRequest(BaseModel):
    items: List[BinderItemRef] = Field(..., min_length=1)

class BinderResponse(BinderBase):
    id: str
    parent_id: Optional[str] = Field(None, validation_alias="parent_uuid")
    user_id: int
    fork_count: int
    original_author_id: Optional[int] = None
    tags: List[TagResponseSchema] = []
    created_at: datetime
    updated_at: datetime
    # True quand le classeur est partagé par un cours/groupe : lecture seule pour l'élève.
    read_only: bool = False
    owner_username: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
