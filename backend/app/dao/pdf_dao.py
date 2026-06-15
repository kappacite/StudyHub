from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.pdf_document import PDFDocument
from app.dao.base_dao import BaseDAO

class PDFDAO(BaseDAO[PDFDocument]):
    def __init__(self, db: Session):
        super().__init__(PDFDocument, db)

    def get_by_id(self, entity_id) -> Optional[PDFDocument]:
        if isinstance(entity_id, int) or (isinstance(entity_id, str) and entity_id.isdigit()):
            from sqlalchemy import or_
            return self.db.query(self.model).filter(or_(self.model._id == int(entity_id), self.model.id == str(entity_id))).first()
        return self.db.query(self.model).filter_by(id=str(entity_id)).first()

    def get_all(self, user_id: int, limit: int = 20, offset: int = 0) -> List[PDFDocument]:
        from sqlalchemy.orm import selectinload
        return (
            self.db.query(self.model)
            .filter_by(user_id=user_id)
            .options(selectinload(self.model.tags), selectinload(self.model.binder))
            .limit(limit)
            .offset(offset)
            .all()
        )

    def get_by_binder_internal_ids(self, binder_internal_ids: List[int]) -> List[PDFDocument]:
        """PDF (tous propriétaires) appartenant aux classeurs donnés — pour le
        contenu en lecture seule des classeurs partagés (cours)."""
        if not binder_internal_ids:
            return []
        from sqlalchemy.orm import selectinload
        return (
            self.db.query(self.model)
            .filter(self.model.binder_id.in_(binder_internal_ids))
            .options(selectinload(self.model.tags), selectinload(self.model.binder))
            .all()
        )

    def get_by_binder(
        self, 
        user_id: int, 
        binder_id = None, 
        tag_id: Optional[int] = None,
        limit: int = 20, 
        offset: int = 0
    ) -> List[PDFDocument]:
        query = self.db.query(self.model).filter_by(user_id=user_id)
        
        if binder_id is not None:
            if isinstance(binder_id, int) or (isinstance(binder_id, str) and binder_id.isdigit()):
                query = query.filter_by(binder_id=int(binder_id))
            else:
                from app.models.binder import Binder
                query = query.join(Binder).filter(Binder.id == str(binder_id))

        if tag_id is not None:
            query = query.filter(self.model.tags.any(id=tag_id))
            
        from sqlalchemy.orm import selectinload
        return query.options(selectinload(self.model.tags), selectinload(self.model.binder)).limit(limit).offset(offset).all()

    def count_by_binder(
        self, 
        user_id: int, 
        binder_id = None,
        tag_id: Optional[int] = None
    ) -> int:
        query = self.db.query(self.model).filter_by(user_id=user_id)
        
        if binder_id is not None:
            if isinstance(binder_id, int) or (isinstance(binder_id, str) and binder_id.isdigit()):
                query = query.filter_by(binder_id=int(binder_id))
            else:
                from app.models.binder import Binder
                query = query.join(Binder).filter(Binder.id == str(binder_id))

        if tag_id is not None:
            query = query.filter(self.model.tags.any(id=tag_id))
            
        return query.count()
