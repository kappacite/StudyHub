from sqlalchemy import Column, Integer, Text, Float, DateTime, ForeignKey, String, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.search_type import TSVectorType
from app.extensions import db

class Flashcard(db.Model):
    __tablename__ = "flashcards"
    __table_args__ = (
        Index('flashcards_search_idx', 'search_vector', postgresql_using='gin'),
    )

    id = Column(Integer, primary_key=True)
    deck_id = Column(Integer, ForeignKey("decks.id", ondelete="CASCADE"), nullable=False)
    front = Column(Text, nullable=False)
    back = Column(Text, nullable=False)
    
    # Placeholders de révision (Active Reading)
    placeholder_hash = Column(String(64), index=True, nullable=True)
    original_text = Column(Text, nullable=True)
    
    # Paramètres de l'algorithme SM-2
    ease_factor = Column(Float, default=2.5, nullable=False)
    interval = Column(Integer, default=0, nullable=False)  # en jours
    repetitions = Column(Integer, default=0, nullable=False)
    next_review = Column(DateTime, server_default=func.now(), nullable=False)
    search_vector = Column(TSVectorType, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relations
    deck = relationship("Deck", back_populates="cards")
