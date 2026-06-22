from typing import List, Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.models.note import Note
from app.dao.base_dao import BaseDAO

class NoteDAO(BaseDAO[Note]):
    def __init__(self, db: Session):
        super().__init__(Note, db)

    def get_by_id(self, entity_id) -> Optional[Note]:
        if isinstance(entity_id, int) or (isinstance(entity_id, str) and entity_id.isdigit()):
            return self.db.query(self.model).filter(or_(self.model._id == int(entity_id), self.model.id == str(entity_id))).first()
        return self.db.query(self.model).filter_by(id=str(entity_id)).first()

    def get_hidden_note_ids(self, user_id: int) -> set:
        """Ids internes des notes masquées par l'utilisateur."""
        from app.models.hidden_note import HiddenNote
        rows = self.db.query(HiddenNote.note_id).filter_by(user_id=user_id).all()
        return {r[0] for r in rows}

    def get_by_binder_internal_ids(self, binder_internal_ids: List[int]) -> List[Note]:
        """Notes (tous propriétaires) appartenant aux classeurs donnés — pour le
        contenu en lecture seule des classeurs partagés."""
        if not binder_internal_ids:
            return []
        from sqlalchemy.orm import selectinload
        return (
            self.db.query(self.model)
            .filter(self.model.binder_id.in_(binder_internal_ids))
            .options(selectinload(self.model.tags), selectinload(self.model.binder))
            .all()
        )

    def get_by_binder_for_user(self, binder_internal_id: int, user_id: int) -> List[Note]:
        """Notes de l'utilisateur appartenant à un classeur donné (id interne)."""
        return (
            self.db.query(self.model)
            .filter(self.model.binder_id == binder_internal_id, self.model.user_id == user_id)
            .all()
        )

    def get_all(self, user_id: int, limit: int = 20, offset: int = 0) -> List[Note]:
        from sqlalchemy.orm import selectinload
        return (
            self.db.query(self.model)
            .filter_by(user_id=user_id)
            .options(selectinload(self.model.tags), selectinload(self.model.binder))
            .limit(limit)
            .offset(offset)
            .all()
        )

    def search_notes(
        self, 
        user_id: int, 
        binder_id = None, 
        search_query: Optional[str] = None,
        tag_id: Optional[int] = None,
        limit: int = 20, 
        offset: int = 0
    ) -> List[Note]:
        query = self.db.query(self.model).filter_by(user_id=user_id)
        
        if binder_id is not None:
            if isinstance(binder_id, int) or (isinstance(binder_id, str) and binder_id.isdigit()):
                query = query.filter_by(binder_id=int(binder_id))
            else:
                from app.models.binder import Binder
                query = query.join(Binder).filter(Binder.id == str(binder_id))
            
        if search_query:
            query = query.filter(
                or_(
                    self.model.title.ilike(f"%{search_query}%"),
                    self.model.content.ilike(f"%{search_query}%")
                )
            )

        if tag_id is not None:
            query = query.filter(self.model.tags.any(id=tag_id))
            
        from sqlalchemy.orm import selectinload
        return query.options(selectinload(self.model.tags), selectinload(self.model.binder)).limit(limit).offset(offset).all()

    def count_notes(
        self, 
        user_id: int, 
        binder_id = None, 
        search_query: Optional[str] = None,
        tag_id: Optional[int] = None
    ) -> int:
        query = self.db.query(self.model).filter_by(user_id=user_id)
        
        if binder_id is not None:
            if isinstance(binder_id, int) or (isinstance(binder_id, str) and binder_id.isdigit()):
                query = query.filter_by(binder_id=int(binder_id))
            else:
                from app.models.binder import Binder
                query = query.join(Binder).filter(Binder.id == str(binder_id))
            
        if search_query:
            query = query.filter(
                or_(
                    self.model.title.ilike(f"%{search_query}%"),
                    self.model.content.ilike(f"%{search_query}%")
                )
            )

        if tag_id is not None:
            query = query.filter(self.model.tags.any(id=tag_id))
            
        return query.count()
