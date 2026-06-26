from typing import List, Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.models.deck import Deck
from app.dao.base_dao import BaseDAO

class DeckDAO(BaseDAO[Deck]):
    def __init__(self, db: Session):
        super().__init__(Deck, db)

    def get_by_binder_internal_ids(self, binder_internal_ids: List[int]) -> List[Deck]:
        """Decks (tous propriétaires) appartenant aux classeurs donnés — pour le
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

    def get_all(self, user_id: int, limit: int = 20, offset: int = 0) -> List[Deck]:
        from sqlalchemy.orm import selectinload
        # On NE charge PAS les cartes : le nombre de cartes est calculé via un
        # COUNT groupé (cf. FlashcardDAO.count_by_decks) pour éviter l'over-fetch.
        return (
            self.db.query(self.model)
            .filter_by(user_id=user_id)
            .options(
                selectinload(self.model.tags),
                selectinload(self.model.binder)
            )
            .limit(limit)
            .offset(offset)
            .all()
        )

    def search_decks(
        self, 
        user_id: int, 
        binder_id: Optional[int] = None, 
        search_query: Optional[str] = None,
        tag_id: Optional[int] = None,
        limit: int = 20, 
        offset: int = 0
    ) -> List[Deck]:
        query = self.db.query(self.model).filter_by(user_id=user_id)
        
        # Filtrer par binder
        if binder_id is not None:
            if isinstance(binder_id, int) or (isinstance(binder_id, str) and binder_id.isdigit()):
                query = query.filter_by(binder_id=int(binder_id))
            else:
                from app.models.binder import Binder
                query = query.join(Binder).filter(Binder.id == str(binder_id))
            
        # Filtrer par recherche
        if search_query:
            query = query.filter(
                or_(
                    self.model.name.ilike(f"%{search_query}%"),
                    self.model.description.ilike(f"%{search_query}%")
                )
            )

        if tag_id is not None:
            query = query.filter(self.model.tags.any(id=tag_id))
            
        from sqlalchemy.orm import selectinload
        # Pas de selectinload(cards) : compte des cartes via COUNT groupé côté service.
        return query.options(
            selectinload(self.model.tags),
            selectinload(self.model.binder)
        ).limit(limit).offset(offset).all()

    def count_decks(
        self, 
        user_id: int, 
        binder_id: Optional[int] = None, 
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
                    self.model.name.ilike(f"%{search_query}%"),
                    self.model.description.ilike(f"%{search_query}%")
                )
            )

        if tag_id is not None:
            query = query.filter(self.model.tags.any(id=tag_id))
            
        return query.count()
