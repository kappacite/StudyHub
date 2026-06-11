from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.diagram import Diagram
from app.dao.base_dao import BaseDAO

class DiagramDAO(BaseDAO[Diagram]):
    def __init__(self, db: Session):
        super().__init__(Diagram, db)

    def get_by_binder(
        self, 
        user_id: int, 
        binder_id: Optional[int] = None, 
        tag_id: Optional[int] = None,
        limit: int = 20, 
        offset: int = 0
    ) -> List[Diagram]:
        query = self.db.query(self.model).filter_by(user_id=user_id)
        
        if binder_id is not None:
            query = query.filter_by(binder_id=binder_id)

        if tag_id is not None:
            query = query.filter(self.model.tags.any(id=tag_id))
            
        return query.limit(limit).offset(offset).all()

    def count_by_binder(
        self, 
        user_id: int, 
        binder_id: Optional[int] = None,
        tag_id: Optional[int] = None
    ) -> int:
        query = self.db.query(self.model).filter_by(user_id=user_id)
        
        if binder_id is not None:
            query = query.filter_by(binder_id=binder_id)

        if tag_id is not None:
            query = query.filter(self.model.tags.any(id=tag_id))
            
        return query.count()
