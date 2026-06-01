from typing import List, Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.models.deck import Deck
from app.dao.base_dao import BaseDAO

class DeckDAO(BaseDAO[Deck]):
    def __init__(self, db: Session):
        super().__init__(Deck, db)

    def search_decks(
        self, 
        user_id: int, 
        binder_id: Optional[int] = None, 
        search_query: Optional[str] = None, 
        limit: int = 20, 
        offset: int = 0
    ) -> List[Deck]:
        query = self.db.query(self.model).filter_by(user_id=user_id)
        
        # Filtrer par binder
        if binder_id is not None:
            query = query.filter_by(binder_id=binder_id)
            
        # Filtrer par recherche
        if search_query:
            query = query.filter(
                or_(
                    self.model.name.ilike(f"%{search_query}%"),
                    self.model.description.ilike(f"%{search_query}%")
                )
            )
            
        return query.limit(limit).offset(offset).all()

    def count_decks(
        self, 
        user_id: int, 
        binder_id: Optional[int] = None, 
        search_query: Optional[str] = None
    ) -> int:
        query = self.db.query(self.model).filter_by(user_id=user_id)
        
        if binder_id is not None:
            query = query.filter_by(binder_id=binder_id)
            
        if search_query:
            query = query.filter(
                or_(
                    self.model.name.ilike(f"%{search_query}%"),
                    self.model.description.ilike(f"%{search_query}%")
                )
            )
            
        return query.count()
