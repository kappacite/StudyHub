from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.extensions import db
from typing import Optional
import uuid

class Binder(db.Model):
    __tablename__ = "binders"

    _id = Column("id", Integer, primary_key=True)
    id = Column("uuid", String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    parent_id = Column(Integer, ForeignKey("binders.id", ondelete="CASCADE"), nullable=True)
    
    # Espace Communautaire & Study Packages
    is_public = Column(Boolean, default=False, nullable=False)
    description = Column(Text, nullable=True)
    fork_count = Column(Integer, default=0, nullable=False)
    original_author_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relations
    user = relationship("User", back_populates="binders", foreign_keys=[user_id])
    original_author = relationship("User", foreign_keys=[original_author_id])
    parent = relationship("Binder", remote_side=[_id], back_populates="children")
    children = relationship("Binder", back_populates="parent", cascade="all, delete-orphan")
    
    decks = relationship("Deck", back_populates="binder", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="binder", cascade="all, delete-orphan")
    diagrams = relationship("Diagram", back_populates="binder", cascade="all, delete-orphan")
    pdfs = relationship("PDFDocument", back_populates="binder", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary="binder_tags", back_populates="binders")

    @property
    def parent_uuid(self) -> Optional[str]:
        return self.parent.id if self.parent else None
