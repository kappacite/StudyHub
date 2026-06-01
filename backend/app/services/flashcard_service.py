from typing import List, Tuple
from app.dao.flashcard_dao import FlashcardDAO
from app.dao.deck_dao import DeckDAO
from app.models.flashcard import Flashcard
from app.schemas.flashcard_schema import FlashcardCreate, FlashcardUpdate, FlashcardResponse
from app.services.spaced_repetition import calculate_sm2
from app.middlewares.error_handler import ResourceNotFoundError, ForbiddenError

class FlashcardService:
    def __init__(self, flashcard_dao: FlashcardDAO, deck_dao: DeckDAO):
        self._flashcard_dao = flashcard_dao
        self._deck_dao = deck_dao

    def _verify_deck_ownership(self, deck_id: int, user_id: int) -> None:
        deck = self._deck_dao.get_by_id(deck_id)
        if not deck:
            raise ResourceNotFoundError("Deck introuvable.")
        if deck.user_id != user_id:
            raise ForbiddenError("Accès interdit à ce deck.")

    def _get_card_or_404(self, card_id: int, deck_id: int, user_id: int) -> Flashcard:
        self._verify_deck_ownership(deck_id, user_id)
        card = self._flashcard_dao.get_by_id(card_id)
        if not card or card.deck_id != deck_id:
            raise ResourceNotFoundError("Flashcard introuvable dans ce deck.")
        return card

    def create_flashcard(self, user_id: int, deck_id: int, data: FlashcardCreate) -> FlashcardResponse:
        self._verify_deck_ownership(deck_id, user_id)
        
        card = Flashcard(
            deck_id=deck_id,
            front=data.front,
            back=data.back
        )
        created = self._flashcard_dao.create(card)
        return FlashcardResponse.model_validate(created)

    def get_flashcards(self, user_id: int, deck_id: int, page: int = 1, per_page: int = 20) -> Tuple[List[FlashcardResponse], int]:
        self._verify_deck_ownership(deck_id, user_id)
        
        offset = (page - 1) * per_page
        cards = self._flashcard_dao.get_by_deck(deck_id, limit=per_page, offset=offset)
        total = self._flashcard_dao.count_by_deck(deck_id)
        
        return [FlashcardResponse.model_validate(c) for c in cards], total

    def get_flashcard(self, user_id: int, deck_id: int, card_id: int) -> FlashcardResponse:
        card = self._get_card_or_404(card_id, deck_id, user_id)
        return FlashcardResponse.model_validate(card)

    def update_flashcard(self, user_id: int, deck_id: int, card_id: int, data: FlashcardUpdate) -> FlashcardResponse:
        card = self._get_card_or_404(card_id, deck_id, user_id)
        
        if data.front is not None:
            card.front = data.front
        if data.back is not None:
            card.back = data.back
            
        updated = self._flashcard_dao.update(card)
        return FlashcardResponse.model_validate(updated)

    def delete_flashcard(self, user_id: int, deck_id: int, card_id: int) -> None:
        card = self._get_card_or_404(card_id, deck_id, user_id)
        self._flashcard_dao.delete(card)

    def get_study_cards(self, user_id: int, deck_id: int) -> List[FlashcardResponse]:
        self._verify_deck_ownership(deck_id, user_id)
        cards = self._flashcard_dao.get_cards_to_study(deck_id)
        return [FlashcardResponse.model_validate(c) for c in cards]

    def answer_card(self, user_id: int, deck_id: int, card_id: int, score: int) -> FlashcardResponse:
        card = self._get_card_or_404(card_id, deck_id, user_id)
        
        # Calcul de la répétition espacée via SM-2
        ease_factor, interval, repetitions, next_review = calculate_sm2(
            score=score,
            ease_factor=card.ease_factor,
            interval=card.interval,
            repetitions=card.repetitions
        )
        
        # Mise à jour de la carte
        card.ease_factor = ease_factor
        card.interval = interval
        card.repetitions = repetitions
        card.next_review = next_review
        
        updated = self._flashcard_dao.update(card)
        return FlashcardResponse.model_validate(updated)
