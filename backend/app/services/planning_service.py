from datetime import datetime, date, timedelta, time
from typing import List, Dict, Any
from app.dao.flashcard_dao import FlashcardDAO
from app.dao.deck_dao import DeckDAO
from app.models.flashcard import Flashcard
from app.middlewares.error_handler import ResourceNotFoundError, ForbiddenError

class PlanningService:
    def __init__(self, flashcard_dao: FlashcardDAO, deck_dao: DeckDAO):
        self._flashcard_dao = flashcard_dao
        self._deck_dao = deck_dao

    def get_calendar(self, user_id: int, date_from: date, date_to: date) -> Dict[str, Any]:
        """
        Calcule la charge de révisions par jour sur une période donnée.
        Les cartes en retard (next_review < date_from) sont rattachées au premier jour (date_from).
        """
        # date_to_dt est la fin de la journée ciblée
        date_to_dt = datetime.combine(date_to, time.max)
        
        # Récupère toutes les cartes dues jusqu'à date_to_dt (inclut l'historique de retard)
        cards = self._flashcard_dao.get_cards_due_between(
            user_id=user_id,
            date_from=datetime.min,
            date_to=date_to_dt
        )
        
        # Initialisation du dictionnaire des jours
        days_data = {}
        current_date = date_from
        while current_date <= date_to:
            days_data[current_date.isoformat()] = {}
            current_date += timedelta(days=1)
            
        # Groupement des cartes par date et par deck
        for card in cards:
            card_review_date = card.next_review.date()
            
            # Les cartes en retard sont comptées le premier jour
            if card_review_date < date_from:
                target_date_str = date_from.isoformat()
            else:
                target_date_str = card_review_date.isoformat()
                
            if target_date_str in days_data:
                deck_id = card.deck_id
                deck_name = card.deck.name if card.deck else "Deck"
                
                if deck_id not in days_data[target_date_str]:
                    days_data[target_date_str][deck_id] = {
                        "deck_id": deck_id,
                        "deck_name": deck_name,
                        "count": 0
                    }
                days_data[target_date_str][deck_id]["count"] += 1
                
        # Formatage final de la réponse
        result = []
        for date_str, decks_dict in sorted(days_data.items()):
            breakdown = list(decks_dict.values())
            total_due = sum(item["count"] for item in breakdown)
            result.append({
                "date": date_str,
                "total_due": total_due,
                "breakdown": breakdown
            })
            
        return {"days": result}

    def advance_review(self, user_id: int, deck_id: int, card_ids: List[int]) -> List[Flashcard]:
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
            
        cards = (
            self._flashcard_dao.db.query(Flashcard)
            .filter(
                Flashcard.deck_id == deck_id,
                Flashcard.id.in_(card_ids)
            )
            .all()
        )
        return cards
