import logging
from typing import List, Tuple, Optional
import uuid
from app.dao.note_dao import NoteDAO
from app.dao.binder_dao import BinderDAO
from app.models.note import Note
from app.schemas.note_schema import NoteCreate, NoteUpdate, NoteResponse
from app.middlewares.error_handler import ResourceNotFoundError, ForbiddenError

logger = logging.getLogger(__name__)

class NoteService:
    def __init__(self, note_dao: NoteDAO, binder_dao: BinderDAO):
        self._note_dao = note_dao
        self._binder_dao = binder_dao

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
        return NoteResponse.model_validate(created)

    def hide_note(self, user_id: int, note_id: int) -> None:
        """Masque une note partagée (de cours) dans la vue de l'utilisateur."""
        note = self._get_note_or_404(note_id, user_id, write_required=False)
        if note.user_id == user_id:
            raise ForbiddenError("Vous ne pouvez masquer qu'une note partagée, pas la vôtre.")
        from app.models.hidden_note import HiddenNote
        db = self._note_dao.db
        existing = db.query(HiddenNote).filter_by(user_id=user_id, note_id=note._id).first()
        if not existing:
            db.add(HiddenNote(user_id=user_id, note_id=note._id))
            db.commit()

    def unhide_note(self, user_id: int, note_id: int) -> None:
        """Réaffiche une note précédemment masquée."""
        note = self._note_dao.get_by_id(note_id)
        if not note:
            raise ResourceNotFoundError("Note introuvable.")
        from app.models.hidden_note import HiddenNote
        db = self._note_dao.db
        existing = db.query(HiddenNote).filter_by(user_id=user_id, note_id=note._id).first()
        if existing:
            db.delete(existing)
            db.commit()

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
        return NoteResponse.model_validate(updated)

    def delete_note(self, user_id: int, note_id: int) -> None:
        note = self._get_note_or_404(note_id, user_id, write_required=True)
        self._note_dao.delete(note)

