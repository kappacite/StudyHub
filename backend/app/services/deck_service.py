from typing import List, Tuple, Optional
from app.dao.deck_dao import DeckDAO
from app.dao.binder_dao import BinderDAO
from app.models.deck import Deck
from app.schemas.deck_schema import DeckCreate, DeckUpdate, DeckResponse
from app.middlewares.error_handler import ResourceNotFoundError, ForbiddenError

class DeckService:
    def __init__(self, deck_dao: DeckDAO, binder_dao: BinderDAO, flashcard_dao=None):
        self._deck_dao = deck_dao
        self._binder_dao = binder_dao
        self._flashcard_dao = flashcard_dao

    def _to_response(self, deck: Deck, card_count: int) -> DeckResponse:
        resp = DeckResponse.model_validate(deck)
        resp.card_count = card_count
        return resp

    def _get_deck_or_404(self, deck_id: int, user_id: int, write_required: bool = False) -> Deck:
        deck = self._deck_dao.get_by_id(deck_id)
        if not deck:
            raise ResourceNotFoundError("Deck introuvable.")
        if deck.user_id != user_id:
            if deck.binder_id:
                from app.utils.security import check_binder_access
                check_binder_access(self._deck_dao.db, deck.binder_id, user_id, write_required=write_required)
            else:
                raise ForbiddenError("Accès interdit à ce deck.")
        elif write_required and deck.binder_id:
            from app.utils.security import check_binder_access
            check_binder_access(self._deck_dao.db, deck.binder_id, user_id, write_required=True)
        return deck

    def create_deck(self, user_id: int, data: DeckCreate) -> DeckResponse:
        binder_id_internal = None
        # Si un binder_id est spécifié, vérifier qu'il appartient bien à l'utilisateur
        if data.binder_id is not None:
            from app.utils.security import check_binder_access
            binder = check_binder_access(self._deck_dao.db, data.binder_id, user_id, write_required=True)
            binder_id_internal = binder._id
                
        deck = Deck(
            name=data.name,
            description=data.description,
            user_id=user_id,
            binder_id=binder_id_internal
        )
        created = self._deck_dao.create(deck)
        return self._to_response(created, 0)

    def get_decks(
        self, 
        user_id: int, 
        binder_id: Optional[int] = None, 
        search: Optional[str] = None, 
        tag_id: Optional[int] = None,
        page: int = 1, 
        per_page: int = 20
    ) -> Tuple[List[DeckResponse], int]:
        offset = (page - 1) * per_page
        decks = self._deck_dao.search_decks(user_id, binder_id, search, tag_id, limit=per_page, offset=offset)
        total = self._deck_dao.count_decks(user_id, binder_id, search, tag_id)

        counts = self._flashcard_dao.count_by_decks([d.id for d in decks])
        return [self._to_response(d, counts.get(d.id, 0)) for d in decks], total

    def get_deck(self, user_id: int, deck_id: int) -> DeckResponse:
        deck = self._get_deck_or_404(deck_id, user_id, write_required=False)
        counts = self._flashcard_dao.count_by_decks([deck.id])
        return self._to_response(deck, counts.get(deck.id, 0))

    def update_deck(self, user_id: int, deck_id: int, data: DeckUpdate) -> DeckResponse:
        deck = self._get_deck_or_404(deck_id, user_id, write_required=True)
        
        if data.name is not None:
            deck.name = data.name
            
        if data.description is not None:
            deck.description = data.description
            
        if data.binder_id is not None:
            from app.utils.security import check_binder_access
            binder = check_binder_access(self._deck_dao.db, data.binder_id, user_id, write_required=True)
            deck.binder_id = binder._id
        elif "binder_id" in data.model_fields_set and data.binder_id is None:
            deck.binder_id = None
            
        updated = self._deck_dao.update(deck)
        counts = self._flashcard_dao.count_by_decks([updated.id])
        return self._to_response(updated, counts.get(updated.id, 0))

    def delete_deck(self, user_id: int, deck_id: int) -> None:
        deck = self._get_deck_or_404(deck_id, user_id, write_required=True)
        self._deck_dao.delete(deck)
