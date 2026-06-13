from datetime import datetime
from typing import Dict, List
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.flashcard import Flashcard
from app.dao.base_dao import BaseDAO

class FlashcardDAO(BaseDAO[Flashcard]):
    def __init__(self, db: Session):
        super().__init__(Flashcard, db)

    def count_by_decks(self, deck_ids: List[int]) -> Dict[int, int]:
        """Compte les cartes par deck en UNE requête (évite l'over-fetch ORM)."""
        if not deck_ids:
            return {}
        rows = (
            self.db.query(self.model.deck_id, func.count(self.model.id))
            .filter(self.model.deck_id.in_(deck_ids))
            .group_by(self.model.deck_id)
            .all()
        )
        return {deck_id: count for deck_id, count in rows}

    def get_by_deck(self, deck_id: int, limit: int = 20, offset: int = 0) -> List[Flashcard]:
        return (
            self.db.query(self.model)
            .filter_by(deck_id=deck_id)
            .limit(limit)
            .offset(offset)
            .all()
        )

    def count_by_deck(self, deck_id: int) -> int:
        return (
            self.db.query(self.model)
            .filter_by(deck_id=deck_id)
            .count()
        )

    def get_cards_to_study(self, deck_id: int) -> List[Flashcard]:
        # Cartes dont la date next_review est passée ou égale à maintenant
        return (
            self.db.query(self.model)
            .filter(
                self.model.deck_id == deck_id,
                self.model.next_review <= datetime.utcnow()
            )
            .all()
        )

    def get_cards_due_between(self, user_id: int, date_from: datetime, date_to: datetime) -> List[Flashcard]:
        from app.models.deck import Deck
        return (
            self.db.query(self.model)
            .join(Deck)
            .filter(
                Deck.user_id == user_id,
                self.model.next_review >= date_from,
                self.model.next_review <= date_to
            )
            .all()
        )
