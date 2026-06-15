from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, selectinload
from app.models.revision import RevisionSet, RevisionItem
from app.dao.base_dao import BaseDAO


class RevisionSetDAO(BaseDAO[RevisionSet]):
    def __init__(self, db: Session):
        super().__init__(RevisionSet, db)

    def search_sets(
        self,
        user_id: int,
        set_type: Optional[str] = None,
        binder_id: Optional[int] = None,
        search_query: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[RevisionSet]:
        query = self.db.query(self.model).filter_by(user_id=user_id)
        if set_type is not None:
            query = query.filter(self.model.type == set_type)
        if binder_id is not None:
            query = query.filter_by(binder_id=binder_id)
        if search_query:
            query = query.filter(
                or_(
                    self.model.name.ilike(f"%{search_query}%"),
                    self.model.description.ilike(f"%{search_query}%"),
                )
            )
        return (
            query.options(selectinload(self.model.binder))
            .order_by(self.model.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

    def count_sets(
        self,
        user_id: int,
        set_type: Optional[str] = None,
        binder_id: Optional[int] = None,
        search_query: Optional[str] = None,
    ) -> int:
        query = self.db.query(self.model).filter_by(user_id=user_id)
        if set_type is not None:
            query = query.filter(self.model.type == set_type)
        if binder_id is not None:
            query = query.filter_by(binder_id=binder_id)
        if search_query:
            query = query.filter(
                or_(
                    self.model.name.ilike(f"%{search_query}%"),
                    self.model.description.ilike(f"%{search_query}%"),
                )
            )
        return query.count()

    def count_items_by_sets(self, set_ids: List[int]) -> Dict[int, int]:
        """Compte les items par ensemble en UNE requête (évite l'over-fetch ORM)."""
        if not set_ids:
            return {}
        rows = (
            self.db.query(RevisionItem.set_id, func.count(RevisionItem.id))
            .filter(RevisionItem.set_id.in_(set_ids))
            .group_by(RevisionItem.set_id)
            .all()
        )
        return {set_id: count for set_id, count in rows}


class RevisionItemDAO(BaseDAO[RevisionItem]):
    def __init__(self, db: Session):
        super().__init__(RevisionItem, db)

    def get_by_set(self, set_id: int, limit: int = 1000, offset: int = 0) -> List[RevisionItem]:
        return (
            self.db.query(self.model)
            .filter_by(set_id=set_id)
            .order_by(self.model.position, self.model.id)
            .limit(limit)
            .offset(offset)
            .all()
        )

    def count_by_set(self, set_id: int) -> int:
        return self.db.query(self.model).filter_by(set_id=set_id).count()

    def get_items_to_study(self, set_id: int) -> List[RevisionItem]:
        return (
            self.db.query(self.model)
            .filter(
                self.model.set_id == set_id,
                self.model.next_review <= datetime.utcnow(),
            )
            .order_by(self.model.position, self.model.id)
            .all()
        )
