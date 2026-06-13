from sqlalchemy import Column, Integer, Text, Float, DateTime, ForeignKey, String, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.search_type import TSVectorType
from app.extensions import db

class Flashcard(db.Model):
    __tablename__ = "flashcards"
    __table_args__ = (
        Index('flashcards_search_idx', 'search_vector', postgresql_using='gin'),
        # Couvre le filtrage par deck (selectinload) ET les cartes dues (next_review).
        Index('ix_flashcards_deck_id_next_review', 'deck_id', 'next_review'),
    )

    id = Column(Integer, primary_key=True)
    deck_id = Column(Integer, ForeignKey("decks.id", ondelete="CASCADE"), nullable=False)
    front = Column(Text, nullable=False)
    back = Column(Text, nullable=False)
    
    # Placeholders de révision (Active Reading)
    placeholder_hash = Column(String(64), index=True, nullable=True)
    original_text = Column(Text, nullable=True)

    # Provenance de la carte : 'manual' = balises de note / création utilisateur
    # (gérée par la sync déterministe du deck fantôme), 'ai' = générée par l'IA
    # (évaluations) et protégée de la sync déterministe.
    source = Column(String(10), default="manual", server_default="manual", nullable=False)
    
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
