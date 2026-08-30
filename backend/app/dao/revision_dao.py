from datetime import datetime

from sqlalchemy import func, or_
from sqlalchemy.orm import Session, selectinload

from app.dao.base_dao import BaseDAO
from app.models.revision import RevisionItem, RevisionSet


class RevisionSetDAO(BaseDAO[RevisionSet]):
    def __init__(self, db: Session):
        super().__init__(RevisionSet, db)

    def search_sets(
        self,
        user_id: int,
        set_type: str | None = None,
        binder_id: int | None = None,
        search_query: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[RevisionSet]:
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
        set_type: str | None = None,
        binder_id: int | None = None,
        search_query: str | None = None,
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

    def get_by_binders(self, binder_ids: list[int]) -> list[RevisionSet]:
        """Tous les ensembles rattachés à l'un des classeurs donnés (PK internes).

        L'accès au classeur (et donc à son sous-arbre) est vérifié en amont par le
        service ; on filtre uniquement par `binder_id` pour couvrir aussi les
        ensembles d'un classeur partagé (qui appartiennent à son propriétaire)."""
        if not binder_ids:
            return []
        return (
            self.db.query(self.model)
            .filter(self.model.binder_id.in_(binder_ids))
            .order_by(self.model.created_at.desc())
            .all()
        )

    def count_items_by_sets(self, set_ids: list[int]) -> dict[int, int]:
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

    def get_by_set(self, set_id: int, limit: int = 1000, offset: int = 0) -> list[RevisionItem]:
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

    def get_by_sets(self, set_ids: list[int]) -> list[RevisionItem]:
        """Tous les items de plusieurs ensembles en UNE requête (anti-N+1, stats classeur)."""
        if not set_ids:
            return []
        return (
            self.db.query(self.model)
            .filter(self.model.set_id.in_(set_ids))
            .order_by(self.model.set_id, self.model.position, self.model.id)
            .all()
        )

    def get_items_to_study(self, set_id: int, include_not_due: bool = False) -> list[RevisionItem]:
        query = self.db.query(self.model).filter_by(set_id=set_id)
        if not include_not_due:
            query = query.filter(self.model.next_review <= datetime.utcnow())
        return query.order_by(self.model.position, self.model.id).all()
