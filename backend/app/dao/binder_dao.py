from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.binder import Binder
from app.dao.base_dao import BaseDAO

class BinderDAO(BaseDAO[Binder]):
    def __init__(self, db: Session):
        super().__init__(Binder, db)

    def get_by_parent(
        self,
        user_id: int,
        parent_id: Optional[int],
        tag_id: Optional[int] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Binder]:
        query = self.db.query(self.model).filter_by(user_id=user_id, parent_id=parent_id)
        if tag_id is not None:
            query = query.filter(self.model.tags.any(id=tag_id))
        return query.limit(limit).offset(offset).all()
        
    def count_by_parent(self, user_id: int, parent_id: Optional[int], tag_id: Optional[int] = None) -> int:
        query = self.db.query(self.model).filter_by(user_id=user_id, parent_id=parent_id)
        if tag_id is not None:
            query = query.filter(self.model.tags.any(id=tag_id))
        return query.count()
