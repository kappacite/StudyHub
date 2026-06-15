from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.extensions import db


class ClassQuestion(db.Model):
    """Question posée par un élève au professeur d'une classe (Q&A) — B4.

    Modèle simple à réponse unique : une question a un corps, un statut
    (`open`/`answered`) et, une fois traitée, la réponse du professeur.
    """
    __tablename__ = "class_questions"
    __table_args__ = (
        Index("ix_class_questions_group_id_created_at", "group_id", "created_at"),
    )

    id          = Column(Integer, primary_key=True)
    group_id    = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False, index=True)
    author_id   = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    body        = Column(Text, nullable=False)
    answer      = Column(Text, nullable=True)
    answered_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    # 'open' tant que sans réponse, 'answered' une fois traitée (= clôturée).
    status      = Column(String(20), nullable=False, default="open", server_default="open")
    created_at  = Column(DateTime, server_default=func.now(), index=True)
    answered_at = Column(DateTime, nullable=True)

    author   = relationship("User", foreign_keys=[author_id])
    answerer = relationship("User", foreign_keys=[answered_by])
