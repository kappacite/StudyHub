from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from app.models.flashcard import Flashcard
from app.dao.base_dao import BaseDAO

class FlashcardDAO(BaseDAO[Flashcard]):
    def __init__(self, db: Session):
        super().__init__(Flashcard, db)

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
