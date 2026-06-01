from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.study_session import StudySession
from app.dao.base_dao import BaseDAO

class StudySessionDAO(BaseDAO[StudySession]):
    def __init__(self, db: Session):
        super().__init__(StudySession, db)

    def get_sessions(
        self, 
        user_id: int, 
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None, 
        module: Optional[str] = None
    ) -> List[StudySession]:
        query = self.db.query(self.model).filter_by(user_id=user_id)
        
        if start_date:
            query = query.filter(self.model.created_at >= start_date)
        if end_date:
            query = query.filter(self.model.created_at <= end_date)
        if module:
            query = query.filter_by(module=module)
            
        return query.order_by(self.model.created_at.desc()).all()

    def get_total_duration(self, user_id: int) -> int:
        result = self.db.query(func.sum(self.model.duration_seconds)).filter_by(user_id=user_id).scalar()
        return result if result else 0

    def get_cards_reviewed_stats(self, user_id: int) -> Dict[str, int]:
        result = (
            self.db.query(
                func.sum(self.model.cards_reviewed),
                func.sum(self.model.cards_correct)
            )
            .filter_by(user_id=user_id)
            .first()
        )
        return {
            "total_reviewed": result[0] if result[0] else 0,
            "total_correct": result[1] if result[1] else 0
        }

    def get_heatmap_data(self, user_id: int, start_date: datetime) -> List[Dict[str, Any]]:
        # Groupement par date (sans l'heure)
        # SQLite vs PostgreSQL : func.date() fonctionne sur les deux.
        date_column = func.date(self.model.created_at)
        
        results = (
            self.db.query(
                date_column.label("date"),
                func.sum(self.model.duration_seconds).label("duration"),
                func.count(self.model.id).label("sessions_count")
            )
            .filter(self.model.user_id == user_id, self.model.created_at >= start_date)
            .group_by(date_column)
            .order_by(date_column.asc())
            .all()
        )
        
        return [
            {
                "date": r.date,
                "duration": int(r.duration),
                "count": r.sessions_count
            }
            for r in results
        ]
