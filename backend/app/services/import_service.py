from datetime import datetime
from typing import Optional, Dict, Any, List
from app.dao.deck_dao import DeckDAO
from app.dao.flashcard_dao import FlashcardDAO
from app.dao.tag_dao import TagDAO
from app.models.deck import Deck
from app.models.flashcard import Flashcard
from app.models.tag import Tag
from app.utils.anki_parser import parse_apkg

class ImportService:
    def __init__(self, deck_dao: DeckDAO, flashcard_dao: FlashcardDAO, tag_dao: TagDAO):
        self._deck_dao = deck_dao
        self._flashcard_dao = flashcard_dao
        self._tag_dao = tag_dao

    def import_anki(self, user_id: int, file_bytes: bytes, binder_id = None) -> Dict[str, Any]:
        """
        Importe les cartes d'une archive Anki (.apkg) dans un nouveau Deck de l'utilisateur.
        """
        # Parse de l'archive Anki
        decks_data, warnings = parse_apkg(file_bytes)
        
        if not decks_data:
            raise ValueError("L'archive Anki ne contient aucun deck valide.")

        # Récupération du nom du deck principal (le premier trouvé)
        main_deck_name = decks_data[0]["name"]
        
        binder_id_internal = None
        if binder_id is not None:
            from app.dao.binder_dao import BinderDAO
            binder = BinderDAO(self._deck_dao.db).get_by_id(binder_id)
            if binder:
                binder_id_internal = binder._id

        # Création du Deck StudyHub
        deck = Deck(
            user_id=user_id,
            name=main_deck_name,
            description="Importé depuis Anki",
            binder_id=binder_id_internal
        )
        
        # Enregistrement du Deck (récupération de l'id)
        deck = self._deck_dao.create(deck)
        
        cards_imported = 0
        cards_skipped = 0
        unique_tags = set()
        
        # Import de toutes les cartes de tous les decks dans le deck unique StudyHub
        for d in decks_data:
            for card_raw in d["cards"]:
                front = card_raw["front"]
                back = card_raw["back"]
                card_tags = card_raw["tags"]
                
                # Ignore les cartes complètement vides
                if not front.strip() and not back.strip():
                    cards_skipped += 1
                    continue
                
                flashcard = Flashcard(
                    deck_id=deck.id,
                    front=front,
                    back=back,
                    ease_factor=2.5,
                    interval=0,
                    repetitions=0,
                    next_review=datetime.utcnow() # Prête pour révision immédiate
                )
                self._flashcard_dao.db.add(flashcard)
                cards_imported += 1
                
                for tag in card_tags:
                    unique_tags.add(tag)
                    
        # Gestion des tags uniques récoltés
        tag_objects: List[Tag] = []
        for tag_name in unique_tags:
            tag_name_clean = tag_name.strip()
            if not tag_name_clean:
                continue
                
            # Vérifie si le tag existe déjà pour cet utilisateur
            tag = self._tag_dao.get_by_name(user_id, tag_name_clean)
            if not tag:
                # Création du tag s'il n'existe pas
                tag = Tag(
                    user_id=user_id,
                    name=tag_name_clean,
                    color="#4F46E5" # Couleur primaire par défaut
                )
                tag = self._tag_dao.create(tag)
            tag_objects.append(tag)
            
        # Liaison des tags au Deck
        if tag_objects:
            deck.tags = tag_objects
            self._deck_dao.update(deck)
        else:
            # Si pas de tags, on doit tout de même commit les flashcards ajoutées au db.session
            self._flashcard_dao.db.commit()
            
        return {
            "deck_id": deck.id,
            "deck_name": deck.name,
            "cards_imported": cards_imported,
            "cards_skipped": cards_skipped,
            "warnings": warnings
        }
