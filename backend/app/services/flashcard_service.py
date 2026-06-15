from typing import List, Tuple
from app.dao.flashcard_dao import FlashcardDAO
from app.dao.deck_dao import DeckDAO
from app.models.flashcard import Flashcard
from app.models.study_session import StudySession
from app.schemas.flashcard_schema import (
    FlashcardCreate, FlashcardUpdate, FlashcardResponse, FlashcardHistoryEntry,
)
from app.services.spaced_repetition import calculate_sm2
from app.middlewares.error_handler import ResourceNotFoundError, ForbiddenError

class FlashcardService:
    def __init__(self, flashcard_dao: FlashcardDAO, deck_dao: DeckDAO):
        self._flashcard_dao = flashcard_dao
        self._deck_dao = deck_dao

    def _verify_deck_ownership(self, deck_id: int, user_id: int, write_required: bool = False) -> None:
        deck = self._deck_dao.get_by_id(deck_id)
        if not deck:
            raise ResourceNotFoundError("Deck introuvable.")
        if deck.user_id != user_id:
            if deck.binder_id:
                from app.utils.security import check_binder_access
                check_binder_access(self._flashcard_dao.db, deck.binder_id, user_id, write_required=write_required)
            else:
                raise ForbiddenError("Accès interdit à ce deck.")
        elif write_required and deck.binder_id:
            from app.utils.security import check_binder_access
            check_binder_access(self._flashcard_dao.db, deck.binder_id, user_id, write_required=True)

    def _get_card_or_404(self, card_id: int, deck_id: int, user_id: int, write_required: bool = False) -> Flashcard:
        self._verify_deck_ownership(deck_id, user_id, write_required=write_required)
        card = self._flashcard_dao.get_by_id(card_id)
        if not card or card.deck_id != deck_id:
            raise ResourceNotFoundError("Flashcard introuvable dans ce deck.")
        return card

    def _create_reverse(self, origin: Flashcard) -> None:
        """Matérialise la carte miroir verso→recto (D7) d'une carte originale."""
        reverse = Flashcard(
            deck_id=origin.deck_id,
            front=origin.back,
            back=origin.front,
            tuning=origin.tuning,
            reverse_of_id=origin.id,
        )
        self._flashcard_dao.create(reverse)

    def create_flashcard(self, user_id: int, deck_id: int, data: FlashcardCreate) -> FlashcardResponse:
        self._verify_deck_ownership(deck_id, user_id, write_required=True)
        deck = self._deck_dao.get_by_id(deck_id)

        card = Flashcard(
            deck_id=deck_id,
            front=data.front,
            back=data.back,
            tuning=data.tuning,
        )
        created = self._flashcard_dao.create(card)
        if deck and deck.reversed:
            self._create_reverse(created)
        return FlashcardResponse.model_validate(created)

    def get_flashcards(self, user_id: int, deck_id: int, page: int = 1, per_page: int = 20) -> Tuple[List[FlashcardResponse], int]:
        self._verify_deck_ownership(deck_id, user_id, write_required=False)
        
        offset = (page - 1) * per_page
        cards = self._flashcard_dao.get_by_deck(deck_id, limit=per_page, offset=offset)
        total = self._flashcard_dao.count_by_deck(deck_id)
        
        return [FlashcardResponse.model_validate(c) for c in cards], total

    def get_flashcard(self, user_id: int, deck_id: int, card_id: int) -> FlashcardResponse:
        card = self._get_card_or_404(card_id, deck_id, user_id, write_required=False)
        return FlashcardResponse.model_validate(card)

    def update_flashcard(self, user_id: int, deck_id: int, card_id: int, data: FlashcardUpdate) -> FlashcardResponse:
        card = self._get_card_or_404(card_id, deck_id, user_id, write_required=True)
        
        if data.front is not None:
            card.front = data.front
        if data.back is not None:
            card.back = data.back
        if data.tuning is not None:
            card.tuning = data.tuning

        updated = self._flashcard_dao.update(card)

        # Garder le miroir inversé synchronisé (contenu + tuning).
        reverse = self._flashcard_dao.get_reverse_for(updated.id)
        if reverse:
            reverse.front = updated.back
            reverse.back = updated.front
            reverse.tuning = updated.tuning
            self._flashcard_dao.update(reverse)

        return FlashcardResponse.model_validate(updated)

    def delete_flashcard(self, user_id: int, deck_id: int, card_id: int) -> None:
        card = self._get_card_or_404(card_id, deck_id, user_id, write_required=True)
        # Supprimer aussi le miroir inversé éventuel.
        reverse = self._flashcard_dao.get_reverse_for(card.id)
        if reverse:
            self._flashcard_dao.delete(reverse)
        self._flashcard_dao.delete(card)

    def get_history(self, user_id: int, deck_id: int, card_id: int) -> List[FlashcardHistoryEntry]:
        self._get_card_or_404(card_id, deck_id, user_id, write_required=False)
        rows = self._flashcard_dao.get_review_history(card_id)
        return [FlashcardHistoryEntry(date=created_at, grade=grade) for created_at, grade in rows]

    def get_study_cards(self, user_id: int, deck_id: int) -> List[FlashcardResponse]:
        self._verify_deck_ownership(deck_id, user_id, write_required=False)
        cards = self._flashcard_dao.get_cards_to_study(deck_id)
        
        # Only keep definitions, true/false, diagram occlusions, and normal cards
        filtered_cards = []
        for c in cards:
            if c.original_text:
                is_def = c.original_text.startswith('[') and ']{def:' in c.original_text
                is_vf = '{{vf::' in c.original_text
                is_qcm = '{{qcm::' in c.original_text
                is_occl = c.original_text.startswith('[diagram:') and 'mask:' in c.original_text
                if is_def or is_vf or is_qcm or is_occl:
                    filtered_cards.append(c)
            else:
                filtered_cards.append(c)
                
        return [FlashcardResponse.model_validate(c) for c in filtered_cards]

    def _card_tuning(self, card: Flashcard) -> float:
        """Tuning effectif d'une carte = tuning du deck × tuning de la carte (D4)."""
        deck = self._deck_dao.get_by_id(card.deck_id)
        deck_tuning = (deck.tuning_default if deck else 1.0) or 1.0
        return deck_tuning * (card.tuning or 1.0)

    def answer_card(self, user_id: int, deck_id: int, card_id: int, score: int) -> FlashcardResponse:
        card = self._get_card_or_404(card_id, deck_id, user_id, write_required=False)

        # Calcul de la répétition espacée via SM-2
        ease_factor, interval, repetitions, next_review = calculate_sm2(
            score=score,
            ease_factor=card.ease_factor,
            interval=card.interval,
            repetitions=card.repetitions,
            tuning=self._card_tuning(card)
        )
        
        # Mise à jour de la carte
        card.ease_factor = ease_factor
        card.interval = interval
        card.repetitions = repetitions
        card.next_review = next_review
        
        updated = self._flashcard_dao.update(card)
        
        # Création d'une StudySession
        study_session = StudySession(
            user_id=user_id,
            module="flashcard",
            duration_seconds=0,
            cards_reviewed=1,
            cards_correct=1 if score >= 3 else 0,
            flashcard_id=card.id,
            grade=score
        )
        self._flashcard_dao.db.add(study_session)
        self._flashcard_dao.db.commit()
        
        # Trigger assignment progress updates
        try:
            from app.services.class_service import trigger_assignment_progress_update
            trigger_assignment_progress_update(self._flashcard_dao.db, user_id, card.id)
        except Exception as e:
            pass
            
        return FlashcardResponse.model_validate(updated)

    def review_card(self, user_id: int, card_id: int, score: int) -> FlashcardResponse:
        card = self._flashcard_dao.get_by_id(card_id)
        if not card:
            raise ResourceNotFoundError("Flashcard introuvable.")
            
        self._verify_deck_ownership(card.deck_id, user_id, write_required=False)

        # Calcul de la répétition espacée via SM-2
        ease_factor, interval, repetitions, next_review = calculate_sm2(
            score=score,
            ease_factor=card.ease_factor,
            interval=card.interval,
            repetitions=card.repetitions,
            tuning=self._card_tuning(card)
        )
        
        # Mise à jour de la carte
        card.ease_factor = ease_factor
        card.interval = interval
        card.repetitions = repetitions
        card.next_review = next_review
        
        updated = self._flashcard_dao.update(card)
        
        # Création d'une StudySession
        study_session = StudySession(
            user_id=user_id,
            module="flashcard",
            duration_seconds=0,
            cards_reviewed=1,
            cards_correct=1 if score >= 3 else 0,
            flashcard_id=card.id,
            grade=score
        )
        self._flashcard_dao.db.add(study_session)
        self._flashcard_dao.db.commit()
        
        # Trigger assignment progress updates
        try:
            from app.services.class_service import trigger_assignment_progress_update
            trigger_assignment_progress_update(self._flashcard_dao.db, user_id, card.id)
        except Exception as e:
            pass
            
        return FlashcardResponse.model_validate(updated)
