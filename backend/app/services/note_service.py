import logging
from typing import List, Tuple, Optional
import uuid
from app.dao.note_dao import NoteDAO
from app.dao.binder_dao import BinderDAO
from app.dao.deck_dao import DeckDAO
from app.dao.flashcard_dao import FlashcardDAO
from app.models.note import Note
from app.models.deck import Deck
from app.models.flashcard import Flashcard
from app.schemas.note_schema import NoteCreate, NoteUpdate, NoteResponse
from app.middlewares.error_handler import ResourceNotFoundError, ForbiddenError
from app.utils.placeholder_parser import extract_placeholders_from_text

logger = logging.getLogger(__name__)

class NoteService:
    def __init__(
        self, 
        note_dao: NoteDAO, 
        binder_dao: BinderDAO,
        deck_dao: Optional[DeckDAO] = None,
        flashcard_dao: Optional[FlashcardDAO] = None
    ):
        self._note_dao = note_dao
        self._binder_dao = binder_dao
        self._deck_dao = deck_dao
        self._flashcard_dao = flashcard_dao

    def _get_note_or_404(self, note_id: int, user_id: int, write_required: bool = False) -> Note:
        note = self._note_dao.get_by_id(note_id)
        if not note:
            raise ResourceNotFoundError("Note introuvable.")
        if note.user_id != user_id:
            if note.binder_id:
                from app.utils.security import check_binder_access
                check_binder_access(self._note_dao.db, note.binder_id, user_id, write_required=write_required)
            else:
                raise ForbiddenError("Accès interdit à cette note.")
        elif write_required and note.binder_id:
            from app.utils.security import check_binder_access
            check_binder_access(self._note_dao.db, note.binder_id, user_id, write_required=True)
        return note


    def create_note(self, user_id: int, data: NoteCreate) -> NoteResponse:
        binder_id_internal = None
        if data.binder_id is not None:
            from app.utils.security import check_binder_access
            binder = check_binder_access(self._note_dao.db, data.binder_id, user_id, write_required=True)
            binder_id_internal = binder._id
                
        from app.utils.html_sanitizer import sanitize_html
        sanitized_content = sanitize_html(data.content)

        note = Note(
            title=data.title,
            content=sanitized_content,
            user_id=user_id,
            binder_id=binder_id_internal
        )
        created = self._note_dao.create(note)
        
        # Synchronisation du deck fantôme
        if self._deck_dao and self._flashcard_dao:
            self._sync_phantom_deck(created)
            
        return NoteResponse.model_validate(created)

    def get_notes(
        self, 
        user_id: int, 
        binder_id: Optional[int] = None, 
        search: Optional[str] = None, 
        tag_id: Optional[int] = None,
        page: int = 1, 
        per_page: int = 20
    ) -> Tuple[List[NoteResponse], int]:
        offset = (page - 1) * per_page
        notes = self._note_dao.search_notes(user_id, binder_id, search, tag_id, limit=per_page, offset=offset)
        total = self._note_dao.count_notes(user_id, binder_id, search, tag_id)

        responses = [NoteResponse.model_validate(n) for n in notes]

        # Lors d'un listing global (sans binder précis), inclure les notes des
        # classeurs partagés par un cours/groupe, en LECTURE SEULE.
        if binder_id is None and search is None and tag_id is None:
            shared_binder_ids: list = []
            for root in self._binder_dao.get_shared_root_binders(user_id):
                shared_binder_ids.append(root._id)
                shared_binder_ids.extend(d._id for d in self._binder_dao.get_descendants(root._id))
            if shared_binder_ids:
                hidden = self._note_dao.get_hidden_note_ids(user_id) if hasattr(self._note_dao, "get_hidden_note_ids") else set()
                for n in self._note_dao.get_by_binder_internal_ids(shared_binder_ids):
                    if n._id in hidden:
                        continue
                    resp = NoteResponse.model_validate(n)
                    resp.read_only = True
                    responses.append(resp)
                total = len(responses)

        return responses, total

    def get_note(self, user_id: int, note_id: int) -> NoteResponse:
        note = self._get_note_or_404(note_id, user_id, write_required=False)
        is_owner = note.user_id == user_id
        # Ne synchroniser le deck fantôme que pour le propriétaire : un élève qui
        # LIT une note partagée ne doit pas déclencher d'écriture sur le deck du prof.
        if is_owner and self._deck_dao and self._flashcard_dao:
            self._sync_phantom_deck(note)
        resp = NoteResponse.model_validate(note)
        resp.read_only = not is_owner
        return resp

    def copy_note(self, user_id: int, note_id: int) -> NoteResponse:
        """Crée une copie personnelle et éditable d'une note accessible (ex. note de
        cours partagée en lecture seule). La copie appartient à l'utilisateur."""
        source = self._get_note_or_404(note_id, user_id, write_required=False)
        from app.utils.html_sanitizer import sanitize_html
        copy = Note(
            title=f"{source.title} (copie)",
            content=sanitize_html(source.content or ""),
            user_id=user_id,
            binder_id=None,  # copie perso, placée à la racine de l'élève
        )
        created = self._note_dao.create(copy)
        if self._deck_dao and self._flashcard_dao:
            self._sync_phantom_deck(created)
        return NoteResponse.model_validate(created)

    def update_note(self, user_id: int, note_id: int, data: NoteUpdate) -> NoteResponse:
        note = self._get_note_or_404(note_id, user_id, write_required=True)
        
        if data.title is not None:
            note.title = data.title
            
        if data.content is not None:
            from app.utils.html_sanitizer import sanitize_html
            note.content = sanitize_html(data.content)
            
        if data.binder_id is not None:
            from app.utils.security import check_binder_access
            binder = check_binder_access(self._note_dao.db, data.binder_id, user_id, write_required=True)
            note.binder_id = binder._id
        elif "binder_id" in data.model_fields_set and data.binder_id is None:
            note.binder_id = None

        # Gestion visibilité publique
        if data.is_public is not None:
            note.is_public = data.is_public
            if data.is_public and not note.share_token:
                note.share_token = uuid.uuid4().hex  # Génère un token unique
            elif not data.is_public:
                note.share_token = None  # Révoque le lien de partage
            
        updated = self._note_dao.update(note)
        
        # Synchronisation du deck fantôme
        if self._deck_dao and self._flashcard_dao:
            self._sync_phantom_deck(updated)
            
        return NoteResponse.model_validate(updated)

    def delete_note(self, user_id: int, note_id: int) -> None:
        note = self._get_note_or_404(note_id, user_id, write_required=True)
        self._note_dao.delete(note)

    def _sync_phantom_deck(self, note: Note) -> None:
        if not self._deck_dao or not self._flashcard_dao:
            return
            
        # 1. Trouver ou créer le deck fantôme pour cette note
        deck = self._deck_dao.db.query(Deck).filter_by(note_id=note._id).first()
        
        deck_name = f"[Phantom] Note: {note.title}"
        deck_desc = f"Deck de révision active pour la note: {note.title}"
        
        if not deck:
            deck = Deck(
                name=deck_name,
                description=deck_desc,
                user_id=note.user_id,
                note_id=note._id,
                binder_id=note.binder_id
            )
            deck = self._deck_dao.create(deck)
        else:
            # Mettre à jour le nom et binder si besoin
            deck.name = deck_name
            deck.description = deck_desc
            deck.binder_id = note.binder_id
            self._deck_dao.update(deck)
            
        # 2. Extraire les placeholders du contenu
        raw_placeholders = extract_placeholders_from_text(note.content, note.id)
        placeholders = [p for p in raw_placeholders if p["type"] in ("def", "qcm", "vf")]
        
        # --- NEW: Extraire les masques de diagrammes intégrés ---
        import re
        import hashlib
        import json
        from app.models.diagram import Diagram
        
        diagram_ids = [int(x) for x in re.findall(r"\[diagram:(\d+)\]", note.content)]
        # Chargement en UNE requête (au lieu d'une par diagramme référencé).
        diagrams_by_id = {
            d.id: d
            for d in self._note_dao.db.query(Diagram).filter(Diagram.id.in_(diagram_ids)).all()
        } if diagram_ids else {}
        for diag_id in diagram_ids:
            diagram = diagrams_by_id.get(diag_id)
            if diagram:
                try:
                    data = json.loads(diagram.code)
                    if isinstance(data, dict) and data.get("type") == "visual":
                        masks = data.get("masks", [])
                        for mask in masks:
                            mask_id = mask.get("id")
                            label = mask.get("label", "")
                            raw_tag = f"[diagram:{diag_id}] mask:{mask_id}"
                            front_text = f"Masque d'occlusion d'image dans le diagramme '{diagram.title}'"
                            p_hash = hashlib.sha256(f"{note.id}:{raw_tag}".encode("utf-8")).hexdigest()
                            
                            placeholders.append({
                                "index": len(placeholders),
                                "raw_tag": raw_tag,
                                "type": "occlusion",
                                "front": front_text,
                                "back": label,
                                "hash": p_hash
                            })
                except Exception as e:
                    logger.warning("Error parsing diagram %s masks: %s", diag_id, e)
        
        # 3. Récupérer les flashcards existantes pour ce deck
        existing_cards = self._flashcard_dao.db.query(Flashcard).filter_by(deck_id=deck.id).all()
        existing_cards_by_hash = {c.placeholder_hash: c for c in existing_cards if c.placeholder_hash}
        
        hashes_in_note = set()
        
        for p in placeholders:
            p_hash = p["hash"]
            hashes_in_note.add(p_hash)
            
            if p_hash in existing_cards_by_hash:
                # Mettre à jour le contenu de la carte si le placeholder a changé
                card = existing_cards_by_hash[p_hash]
                card.front = p["front"]
                card.back = p["back"]
                card.original_text = p["raw_tag"]
                self._flashcard_dao.update(card)
            else:
                # Créer une nouvelle carte
                card = Flashcard(
                    deck_id=deck.id,
                    front=p["front"],
                    back=p["back"],
                    placeholder_hash=p_hash,
                    original_text=p["raw_tag"]
                )
                self._flashcard_dao.create(card)
                
        # 4. Supprimer les cartes obsolètes
        for p_hash, card in existing_cards_by_hash.items():
            if p_hash not in hashes_in_note:
                self._flashcard_dao.delete(card)
