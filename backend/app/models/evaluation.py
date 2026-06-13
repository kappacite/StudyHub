from sqlalchemy import (
    Column, Integer, Float, String, DateTime, ForeignKey, JSON, Boolean, Index,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.extensions import db


class Evaluation(db.Model):
    """Feuille d'évaluation d'une note : agrège des items hétérogènes (qcm, vf,
    trou, open) générés par l'IA en un seul appel et/ou issus des balises de la
    note. `content_hash` permet de ne pas régénérer l'IA tant que la note n'a
    pas changé (cache)."""

    __tablename__ = "evaluations"
    __table_args__ = (
        Index("ix_evaluations_note_id", "note_id"),
        Index("ix_evaluations_user_id", "user_id"),
    )

    id = Column(Integer, primary_key=True)
    note_id = Column(Integer, ForeignKey("notes.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    # Hash du contenu de la note au moment de la génération IA (cache / fraîcheur).
    content_hash = Column(String(64), nullable=True)
    score_pct = Column(Float, nullable=True)  # null = non complétée
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)

    # Relations
    note = relationship("Note")
    user = relationship("User")
    items = relationship(
        "EvaluationItem",
        back_populates="evaluation",
        cascade="all, delete-orphan",
        order_by="EvaluationItem.id",
    )


class EvaluationItem(db.Model):
    """Un item d'une feuille d'évaluation. `payload` JSON absorbe les schémas
    hétérogènes selon `type` (clé de correction embarquée). `user_answer` stocke
    la réponse saisie et, pour les items 'open', le niveau d'auto-évaluation."""

    __tablename__ = "evaluation_items"
    __table_args__ = (
        Index("ix_evaluation_items_evaluation_id", "evaluation_id"),
    )

    id = Column(Integer, primary_key=True)
    evaluation_id = Column(
        Integer, ForeignKey("evaluations.id", ondelete="CASCADE"), nullable=False
    )
    type = Column(String(10), nullable=False)  # 'qcm' | 'vf' | 'trou' | 'open'
    # Provenance : 'ai' (générée par Gemini) ou 'manual' (balise de note).
    source = Column(String(10), default="ai", server_default="ai", nullable=False)
    # Question + clé de correction, selon le type (cf. ai_service.generate_evaluation).
    payload = Column(JSON, nullable=False)
    # Réponse de l'étudiant : { "value": ..., "self_grade": "acquired|partial|missed" }.
    user_answer = Column(JSON, nullable=True)
    is_correct = Column(Boolean, nullable=True)  # rempli à la correction

    # Relations
    evaluation = relationship("Evaluation", back_populates="items")
