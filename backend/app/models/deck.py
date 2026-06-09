from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.extensions import db

class Deck(db.Model):
    __tablename__ = "decks"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    binder_id = Column(Integer, ForeignKey("binders.id", ondelete="SET NULL"), nullable=True)
    note_id = Column(Integer, ForeignKey("notes.id", ondelete="CASCADE"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relations
    user = relationship("User", back_populates="decks")
    binder = relationship("Binder", back_populates="decks")
    note = relationship("Note", back_populates="deck", foreign_keys=[note_id])
    cards = relationship("Flashcard", back_populates="deck", cascade="all, delete-orphan")

    @property
    def card_count(self) -> int:
        return len(self.cards)
