from typing import Optional
from sqlalchemy.orm import Session
from app.models.note_grade import NoteGrade
from app.dao.base_dao import BaseDAO


class NoteGradeDAO(BaseDAO[NoteGrade]):
    def __init__(self, db: Session):
        super().__init__(NoteGrade, db)

    def get_by_note(self, note_internal_id: int) -> Optional[NoteGrade]:
        return self.db.query(self.model).filter_by(note_id=note_internal_id).first()

    def upsert(self, note_internal_id: int, user_id: int, data: dict) -> NoteGrade:
        """Cree ou ecrase la notation d'une note (pas d'historique -- une reevaluation
        remplace la precedente, cf. CONTEXT.md notes-ia-planning-corrections)."""
        existing = self.get_by_note(note_internal_id)
        if existing:
            existing.score = data["score"]
            existing.verdict = data["verdict"]
            existing.points_forts = data["points_forts"]
            existing.ameliorations = data["ameliorations"]
            existing.suggestions = data.get("suggestions")
            self.db.commit()
            return existing

        grade = NoteGrade(
            note_id=note_internal_id,
            user_id=user_id,
            score=data["score"],
            verdict=data["verdict"],
            points_forts=data["points_forts"],
            ameliorations=data["ameliorations"],
            suggestions=data.get("suggestions"),
        )
        self.db.add(grade)
        self.db.commit()
        return grade
