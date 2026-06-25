from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.quiz import Quiz, QuizQuestion
from app.dao.base_dao import BaseDAO

class QuizDAO(BaseDAO[Quiz]):
    def __init__(self, db: Session):
        super().__init__(Quiz, db)

    def get_by_user(self, user_id: int, limit: int = 20, offset: int = 0) -> List[Quiz]:
        return (
            self.db.query(self.model)
            .filter_by(user_id=user_id)
            .order_by(self.model.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

    def get_by_note(self, note_id: int) -> List[Quiz]:
        return (
            self.db.query(self.model)
            .filter_by(note_id=note_id)
            .order_by(self.model.created_at.desc())
            .all()
        )

    def get_by_note_and_user(self, note_id: int, user_id: int) -> List[Quiz]:
        """Quiz d'un utilisateur pour une note donnée (isolation : indispensable
        pour les notes partagées, où plusieurs lecteurs génèrent leurs propres quiz)."""
        return (
            self.db.query(self.model)
            .filter_by(note_id=note_id, user_id=user_id)
            .order_by(self.model.created_at.desc())
            .all()
        )

    def get_best_completed_for_note(self, note_id: int, user_id: int) -> Optional[Quiz]:
        """Meilleur quiz complété par l'utilisateur pour une note (score max)."""
        return (
            self.db.query(self.model)
            .filter(
                self.model.note_id == note_id,
                self.model.user_id == user_id,
                self.model.completed_at.isnot(None),
            )
            .order_by(self.model.score_pct.desc().nullslast())
            .first()
        )

    def get_question(self, question_id: int) -> Optional[QuizQuestion]:
        return self.db.get(QuizQuestion, question_id)

    def save_question(self, question: QuizQuestion) -> QuizQuestion:
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        return question
