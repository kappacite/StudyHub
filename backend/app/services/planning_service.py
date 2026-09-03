from datetime import datetime, date, timedelta, time
from typing import List, Dict, Any, Optional
from app.dao.flashcard_dao import FlashcardDAO
from app.dao.deck_dao import DeckDAO
from app.dao.revision_dao import RevisionItemDAO, RevisionSetDAO
from app.models.flashcard import Flashcard
from app.models.revision import RevisionItem
from app.middlewares.error_handler import ResourceNotFoundError, ForbiddenError

class PlanningService:
    def __init__(
        self,
        flashcard_dao: FlashcardDAO,
        deck_dao: DeckDAO,
        revision_item_dao: RevisionItemDAO,
        revision_set_dao: RevisionSetDAO,
    ):
        self._flashcard_dao = flashcard_dao
        self._deck_dao = deck_dao
        self._revision_item_dao = revision_item_dao
        self._revision_set_dao = revision_set_dao

    def get_calendar(self, user_id: int, date_from: date, date_to: date) -> Dict[str, Any]:
        """
        Calcule la charge de révisions par jour sur une période donnée : decks de flashcards
        ET ensembles de révision (RevisionSet/RevisionItem), agrégés ensemble (notes-ia-
        planning-corrections, Task 1 -- les ensembles n'étaient jusque-là jamais comptés,
        planning vide en permanence pour un compte qui étudie surtout via des ensembles).
        Les items en retard (next_review < date_from) sont rattachés au premier jour (date_from).
        """
        # date_to_dt est la fin de la journée ciblée
        date_to_dt = datetime.combine(date_to, time.max)

        cards = self._flashcard_dao.get_cards_due_between(
            user_id=user_id,
            date_from=datetime.min,
            date_to=date_to_dt
        )
        revision_items = self._revision_item_dao.get_items_due_between(
            user_id=user_id,
            date_from=datetime.min,
            date_to=date_to_dt,
        )

        # Initialisation du dictionnaire des jours
        days_data = {}
        current_date = date_from
        while current_date <= date_to:
            days_data[current_date.isoformat()] = {}
            current_date += timedelta(days=1)

        def _bucket_date(review_dt: datetime) -> Optional[str]:
            review_date = review_dt.date()
            target = date_from if review_date < date_from else review_date
            target_str = target.isoformat()
            return target_str if target_str in days_data else None

        for card in cards:
            target_date_str = _bucket_date(card.next_review)
            if target_date_str is None:
                continue
            key = ("deck", card.deck_id)
            bucket = days_data[target_date_str]
            if key not in bucket:
                bucket[key] = {
                    "kind": "deck",
                    "id": card.deck_id,
                    "name": card.deck.name if card.deck else "Deck",
                    "count": 0,
                }
            bucket[key]["count"] += 1

        for item in revision_items:
            target_date_str = _bucket_date(item.next_review)
            if target_date_str is None:
                continue
            key = ("revision_set", item.set_id)
            bucket = days_data[target_date_str]
            if key not in bucket:
                bucket[key] = {
                    "kind": "revision_set",
                    "id": item.set_id,
                    "name": item.revision_set.name if item.revision_set else "Ensemble",
                    "count": 0,
                }
            bucket[key]["count"] += 1

        # Formatage final de la réponse
        result = []
        for date_str, items_dict in sorted(days_data.items()):
            breakdown = list(items_dict.values())
            total_due = sum(item["count"] for item in breakdown)
            result.append({
                "date": date_str,
                "total_due": total_due,
                "breakdown": breakdown
            })

        return {"days": result}

    def advance_review(self, user_id: int, deck_id: int, card_ids: Optional[List[int]] = None, date_str: Optional[str] = None) -> List[Flashcard]:
        """
        Valide la demande de révision anticipée et retourne les cartes concernées.

        Note sur la règle métier :
        Quand un étudiant révise une carte avant sa next_review (en avance), l'algorithme SM-2
        s'applique normalement mais repart de la date du jour (today) et non de l'ancienne next_review.
        C'est le comportement par défaut de spaced_repetition.py qui utilise datetime.utcnow().
        """
        deck = self._deck_dao.get_by_id(deck_id)
        if not deck:
            raise ResourceNotFoundError("Deck introuvable.")
        if deck.user_id != user_id:
            raise ForbiddenError("Accès interdit à ce deck.")

        if card_ids:
            cards = (
                self._flashcard_dao.db.query(Flashcard)
                .filter(
                    Flashcard.deck_id == deck_id,
                    Flashcard.id.in_(card_ids)
                )
                .all()
            )
        elif date_str:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            date_start = datetime.combine(target_date, time.min)
            date_end = datetime.combine(target_date, time.max)
            cards = (
                self._flashcard_dao.db.query(Flashcard)
                .filter(
                    Flashcard.deck_id == deck_id,
                    Flashcard.next_review >= date_start,
                    Flashcard.next_review <= date_end
                )
                .all()
            )
        else:
            cards = []

        return cards

    def advance_review_set(
        self, user_id: int, set_id: int,
        item_ids: Optional[List[int]] = None, date_str: Optional[str] = None,
    ) -> List[RevisionItem]:
        """Équivalent de advance_review, pour un RevisionSet (notes-ia-planning-corrections,
        Task 1). Même règle : ne modifie rien, se contente de retourner les items concernés."""
        rset = self._revision_set_dao.get_by_id(set_id)
        if not rset:
            raise ResourceNotFoundError("Ensemble de révision introuvable.")
        if rset.user_id != user_id:
            raise ForbiddenError("Accès interdit à cet ensemble.")

        if item_ids:
            items = (
                self._revision_item_dao.db.query(RevisionItem)
                .filter(
                    RevisionItem.set_id == set_id,
                    RevisionItem.id.in_(item_ids),
                )
                .all()
            )
        elif date_str:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            date_start = datetime.combine(target_date, time.min)
            date_end = datetime.combine(target_date, time.max)
            items = (
                self._revision_item_dao.db.query(RevisionItem)
                .filter(
                    RevisionItem.set_id == set_id,
                    RevisionItem.next_review >= date_start,
                    RevisionItem.next_review <= date_end,
                )
                .all()
            )
        else:
            items = []

        return items
