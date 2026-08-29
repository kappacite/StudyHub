from datetime import datetime
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.dao.base_dao import BaseDAO
from app.models.study_session import StudySession


class StudySessionDAO(BaseDAO[StudySession]):
    def __init__(self, db: Session):
        super().__init__(StudySession, db)

    def get_sessions(
        self,
        user_id: int,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        module: str | None = None,
    ) -> list[StudySession]:
        query = self.db.query(self.model).filter_by(user_id=user_id)

        if start_date:
            query = query.filter(self.model.created_at >= start_date)
        if end_date:
            query = query.filter(self.model.created_at <= end_date)
        if module:
            query = query.filter_by(module=module)

        return query.order_by(self.model.created_at.desc()).all()

    def get_for_item(
        self, item_id: int, item_type: str, user_id: int | None = None
    ) -> list[StudySession]:
        """Historique des sessions d'un élément de révision, ordre chronologique.

        `user_id` est optionnel : un ensemble partagé (« cours ») laisse plusieurs
        utilisateurs enregistrer des StudySession sur les mêmes items (cf.
        revision_service.py, SM-2 partagé) ; ne pas le fournir renvoie donc
        l'historique agrégé de tous les utilisateurs. Les appelants qui affichent
        des stats *personnelles* (revision_stats_service.py) doivent le fournir
        pour ne pas montrer/compter les sessions d'autrui.
        """
        query = self.db.query(self.model).filter(
            self.model.item_id == item_id, self.model.item_type == item_type
        )
        if user_id is not None:
            query = query.filter(self.model.user_id == user_id)
        return query.order_by(self.model.created_at.asc()).all()

    def get_for_items(
        self, item_ids: list[int], item_type: str, user_id: int | None = None
    ) -> list[StudySession]:
        """Sessions de plusieurs éléments (agrégats par ensemble, anti-N+1).

        Voir `get_for_item` pour la sémantique de `user_id` (optionnel).
        """
        if not item_ids:
            return []
        query = self.db.query(self.model).filter(
            self.model.item_id.in_(item_ids), self.model.item_type == item_type
        )
        if user_id is not None:
            query = query.filter(self.model.user_id == user_id)
        return query.order_by(self.model.created_at.asc()).all()

    def get_total_duration(self, user_id: int) -> int:
        result = (
            self.db.query(func.sum(self.model.duration_seconds)).filter_by(user_id=user_id).scalar()
        )
        return result if result else 0

    def get_cards_reviewed_stats(self, user_id: int) -> dict[str, int]:
        result = (
            self.db.query(func.sum(self.model.cards_reviewed), func.sum(self.model.cards_correct))
            .filter_by(user_id=user_id)
            .first()
        )
        return {
            "total_reviewed": result[0] if result[0] else 0,
            "total_correct": result[1] if result[1] else 0,
        }

    def get_heatmap_data(self, user_id: int, start_date: datetime) -> list[dict[str, Any]]:
        # Groupement par date (sans l'heure)
        # SQLite vs PostgreSQL : func.date() fonctionne sur les deux.
        date_column = func.date(self.model.created_at)

        results = (
            self.db.query(
                date_column.label("date"),
                func.sum(self.model.duration_seconds).label("duration"),
                func.count(self.model.id).label("sessions_count"),
            )
            .filter(self.model.user_id == user_id, self.model.created_at >= start_date)
            .group_by(date_column)
            .order_by(date_column.asc())
            .all()
        )

        return [
            {
                # PostgreSQL renvoie un datetime.date, SQLite une str : on normalise.
                "date": r.date if isinstance(r.date, str) else r.date.isoformat(),
                "duration": int(r.duration),
                "count": r.sessions_count,
            }
            for r in results
        ]
