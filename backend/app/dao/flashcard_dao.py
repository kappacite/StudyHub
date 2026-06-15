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
        """Compte les cartes *originales* par deck en UNE requête (les miroirs
        inversés, reverse_of_id non nul, ne sont pas comptés)."""
        if not deck_ids:
            return {}
        rows = (
            self.db.query(self.model.deck_id, func.count(self.model.id))
            .filter(self.model.deck_id.in_(deck_ids))
            .filter(self.model.reverse_of_id.is_(None))
            .group_by(self.model.deck_id)
            .all()
        )
        return {deck_id: count for deck_id, count in rows}

    def get_by_deck(self, deck_id: int, limit: int = 20, offset: int = 0) -> List[Flashcard]:
        # Liste de gestion : cartes originales uniquement (les miroirs inversés
        # sont gérés via le mode inversé du deck, pas éditables séparément).
        return (
            self.db.query(self.model)
            .filter_by(deck_id=deck_id)
            .filter(self.model.reverse_of_id.is_(None))
            .limit(limit)
            .offset(offset)
            .all()
        )

    def count_by_deck(self, deck_id: int) -> int:
        return (
            self.db.query(self.model)
            .filter_by(deck_id=deck_id)
            .filter(self.model.reverse_of_id.is_(None))
            .count()
        )

    def get_originals_by_deck(self, deck_id: int) -> List[Flashcard]:
        return (
            self.db.query(self.model)
            .filter_by(deck_id=deck_id)
            .filter(self.model.reverse_of_id.is_(None))
            .all()
        )

    def get_reverses_by_deck(self, deck_id: int) -> List[Flashcard]:
        return (
            self.db.query(self.model)
            .filter_by(deck_id=deck_id)
            .filter(self.model.reverse_of_id.isnot(None))
            .all()
        )

    def get_reverse_for(self, origin_id: int) -> "Flashcard | None":
        return self.db.query(self.model).filter_by(reverse_of_id=origin_id).first()

    def get_review_history(self, card_id: int) -> List["tuple"]:
        """Historique (date, grade) des révisions d'une carte (courbe d'apprentissage)."""
        from app.models.study_session import StudySession
        return (
            self.db.query(StudySession.created_at, StudySession.grade)
            .filter(StudySession.flashcard_id == card_id)
            .order_by(StudySession.created_at)
            .all()
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
        from sqlalchemy.orm import joinedload
        return (
            self.db.query(self.model)
            .join(Deck)
            # Le planning lit card.deck.name : on charge le deck pour éviter le N+1.
            .options(joinedload(self.model.deck))
            .filter(
                Deck.user_id == user_id,
                self.model.next_review >= date_from,
                self.model.next_review <= date_to
            )
            .all()
        )
