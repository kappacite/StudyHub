from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.exam import ExamSession
from app.dao.base_dao import BaseDAO

class ExamDAO(BaseDAO[ExamSession]):
    def __init__(self, db: Session):
        super().__init__(ExamSession, db)

    def get_by_user(self, user_id: int, limit: int = 20, offset: int = 0) -> List[ExamSession]:
        return (
            self.db.query(self.model)
            .filter_by(user_id=user_id)
            .order_by(self.model.started_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

    def get_best_completed_for_binder(self, binder_id: int, user_id: int) -> Optional[ExamSession]:
        """Meilleur examen complété par l'utilisateur pour un classeur (score max)."""
        return (
            self.db.query(self.model)
            .filter(
                self.model.binder_id == binder_id,
                self.model.user_id == user_id,
                self.model.completed_at.isnot(None),
            )
            .order_by(self.model.score_pct.desc().nullslast())
            .first()
        )

    def get_active_sessions(self, user_id: int) -> List[ExamSession]:
        return (
            self.db.query(self.model)
            .filter_by(user_id=user_id, completed_at=None)
            .order_by(self.model.started_at.desc())
            .all()
        )
