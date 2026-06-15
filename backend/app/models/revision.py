from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, ForeignKey, Index, JSON, Boolean
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from typing import Optional
from app.extensions import db

# Types d'ensembles de révision *génériques* (hors flashcard, qui reste un Deck).
# Décision d'archi D3c : « flashcard » = recto/verso dans un Deck ; les autres
# types de révision sont des entités indépendantes portées par RevisionSet.
REVISION_SET_TYPES = ("qcm", "vf", "association", "definition", "ordre")


class RevisionSet(db.Model):
    """Ensemble de révision *homogène* (un seul type), rattaché à un classeur.

    Pendant générique du `Deck` (réservé, lui, aux flashcards recto/verso).
    Tous les items d'un ensemble partagent son `type`.
    """

    __tablename__ = "revision_sets"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    # Type homogène de l'ensemble (cf. REVISION_SET_TYPES).
    type = Column(String(20), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    binder_id = Column(Integer, ForeignKey("binders.id", ondelete="SET NULL"), nullable=True, index=True)
    # Multiplicateur SM-2 par défaut appliqué aux items de l'ensemble (D4).
    tuning_default = Column(Float, default=1.0, server_default="1.0", nullable=False)
    is_public = Column(Boolean, default=False, server_default="0", nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relations
    user = relationship("User", back_populates="revision_sets")
    binder = relationship("Binder", back_populates="revision_sets")
    items = relationship(
        "RevisionItem", back_populates="revision_set", cascade="all, delete-orphan"
    )

    @property
    def binder_uuid(self) -> Optional[str]:
        return self.binder.id if self.binder else None


class RevisionItem(db.Model):
    """Item d'un ensemble de révision, avec son propre état SM-2.

    Le contenu structuré vit dans `payload`, validé selon le type de l'ensemble :
      qcm         -> {"question", "options": [{"id","text","correct"}], "points": int}
      vf          -> {"assertion", "correct": bool, "justification"}
      association -> {"title", "pairs": [{"left","right"}]}
      definition  -> {"term", "definition"}
      ordre       -> {"title", "steps": [...]}  (ordre correct)
    """

    __tablename__ = "revision_items"
    __table_args__ = (
        # Couvre le filtrage par ensemble ET les items dus (next_review).
        Index("ix_revision_items_set_id_next_review", "set_id", "next_review"),
    )

    id = Column(Integer, primary_key=True)
    set_id = Column(Integer, ForeignKey("revision_sets.id", ondelete="CASCADE"), nullable=False)
    payload = Column(JSON, nullable=False)
    # Position d'affichage (ex. ordre des items dans l'éditeur).
    position = Column(Integer, default=0, server_default="0", nullable=False)

    # Multiplicateur SM-2 par item (« s'acharner » ou espacer une carte) — D4.
    tuning = Column(Float, default=1.0, server_default="1.0", nullable=False)

    # Paramètres de l'algorithme SM-2 (alignés sur Flashcard).
    ease_factor = Column(Float, default=2.5, nullable=False)
    interval = Column(Integer, default=0, nullable=False)  # en jours
    repetitions = Column(Integer, default=0, nullable=False)
    next_review = Column(DateTime, server_default=func.now(), nullable=False)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relations
    revision_set = relationship("RevisionSet", back_populates="items")
