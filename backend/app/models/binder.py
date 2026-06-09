from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.extensions import db

class Binder(db.Model):
    __tablename__ = "binders"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    parent_id = Column(Integer, ForeignKey("binders.id", ondelete="CASCADE"), nullable=True)
    
    # Espace Communautaire & Study Packages
    is_public = Column(Boolean, default=False, nullable=False)
    description = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)  # Stocke une liste de tags
    fork_count = Column(Integer, default=0, nullable=False)
    original_author_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relations
    user = relationship("User", back_populates="binders", foreign_keys=[user_id])
    original_author = relationship("User", foreign_keys=[original_author_id])
    parent = relationship("Binder", remote_side=[id], back_populates="children")
    children = relationship("Binder", back_populates="parent", cascade="all, delete-orphan")
    
    decks = relationship("Deck", back_populates="binder", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="binder", cascade="all, delete-orphan")
    diagrams = relationship("Diagram", back_populates="binder", cascade="all, delete-orphan")
    pdfs = relationship("PDFDocument", back_populates="binder", cascade="all, delete-orphan")
