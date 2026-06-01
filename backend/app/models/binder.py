from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.extensions import db

class Binder(db.Model):
    __tablename__ = "binders"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    parent_id = Column(Integer, ForeignKey("binders.id", ondelete="CASCADE"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relations
    user = relationship("User", back_populates="binders")
    parent = relationship("Binder", remote_side=[id], back_populates="children")
    children = relationship("Binder", back_populates="parent", cascade="all, delete-orphan")
    
    decks = relationship("Deck", back_populates="binder", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="binder", cascade="all, delete-orphan")
    diagrams = relationship("Diagram", back_populates="binder", cascade="all, delete-orphan")
    pdfs = relationship("PDFDocument", back_populates="binder", cascade="all, delete-orphan")
