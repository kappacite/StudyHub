from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.search_type import TSVectorType
from app.extensions import db

class Deck(db.Model):
    __tablename__ = "decks"
    __table_args__ = (
        Index('decks_search_idx', 'search_vector', postgresql_using='gin'),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    binder_id = Column(Integer, ForeignKey("binders.id", ondelete="SET NULL"), nullable=True)
    note_id = Column(Integer, ForeignKey("notes.id", ondelete="CASCADE"), nullable=True)
    search_vector = Column(TSVectorType, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relations
    user = relationship("User", back_populates="decks")
    binder = relationship("Binder", back_populates="decks")
    note = relationship("Note", back_populates="deck", foreign_keys=[note_id])
    cards = relationship("Flashcard", back_populates="deck", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary="deck_tags", back_populates="decks")

    @property
    def card_count(self) -> int:
        return len(self.cards)
