from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, JSON, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.extensions import db


class NoteGrade(db.Model):
    """Notation IA de la qualite d'une fiche (score/verdict/points forts/ameliorations/
    suggestions) -- une par note, ecrasee a chaque reevaluation (pas d'historique,
    notes-ia-planning-corrections Task 12). A distinguer de Evaluation, qui note la
    performance de l'etudiant sur des exercices generes, pas la fiche elle-meme."""

    __tablename__ = "note_grades"
    __table_args__ = (
        Index("ix_note_grades_note_id", "note_id", unique=True),
    )

    id = Column(Integer, primary_key=True)
    note_id = Column(Integer, ForeignKey("notes.id", ondelete="CASCADE"), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    score = Column(Integer, nullable=False)
    verdict = Column(Text, nullable=False)
    points_forts = Column(JSON, nullable=False, default=list)
    ameliorations = Column(JSON, nullable=False, default=list)
    suggestions = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    note = relationship("Note")
