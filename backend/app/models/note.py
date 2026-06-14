from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.models.search_type import TSVectorType
from app.extensions import db
from typing import Optional

class Note(db.Model):
    __tablename__ = "notes"
    __table_args__ = (
        Index('notes_search_idx', 'search_vector', postgresql_using='gin'),
    )

    _id = Column("id", Integer, primary_key=True)
    id = Column("uuid", String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    content = Column(Text, default="", nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    binder_id = Column(Integer, ForeignKey("binders.id", ondelete="SET NULL"), nullable=True, index=True)
    is_public = Column(Boolean, default=False, nullable=False)
    share_token = Column(String(64), unique=True, nullable=True, index=True)
    last_blurting_at = Column(DateTime, nullable=True)
    search_vector = Column(TSVectorType, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relations
    user = relationship("User", back_populates="notes")
    binder = relationship("Binder", back_populates="notes")
    tags = relationship("Tag", secondary="note_tags", back_populates="notes")

    @property
    def binder_uuid(self) -> Optional[str]:
        return self.binder.id if self.binder else None
