from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Index
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
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    binder_id = Column(Integer, ForeignKey("binders.id", ondelete="SET NULL"), nullable=True, index=True)
    # Mode inversé (D7) : si vrai, chaque carte recto/verso a une carte miroir
    # verso→recto (Flashcard.reverse_of_id) avec son propre état SM-2.
    reversed = Column(Boolean, default=False, server_default="0", nullable=False)
    # Multiplicateur SM-2 par défaut des cartes du deck (D4).
    tuning_default = Column(Float, default=1.0, server_default="1.0", nullable=False)
    search_vector = Column(TSVectorType, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relations
    user = relationship("User", back_populates="decks")
    binder = relationship("Binder", back_populates="decks")
    cards = relationship("Flashcard", back_populates="deck", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary="deck_tags", back_populates="decks")
    # NB : le nombre de cartes (`card_count` de DeckResponse) est injecté par le
    # service via un COUNT groupé — pas de propriété `len(self.cards)` ici (over-fetch).
