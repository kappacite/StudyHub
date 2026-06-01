from typing import List, Tuple, Optional
from app.dao.note_dao import NoteDAO
from app.dao.binder_dao import BinderDAO
from app.models.note import Note
from app.schemas.note_schema import NoteCreate, NoteUpdate, NoteResponse
from app.middlewares.error_handler import ResourceNotFoundError, ForbiddenError

class NoteService:
    def __init__(self, note_dao: NoteDAO, binder_dao: BinderDAO):
        self._note_dao = note_dao
        self._binder_dao = binder_dao

    def _get_note_or_404(self, note_id: int, user_id: int) -> Note:
        note = self._note_dao.get_by_id(note_id)
        if not note:
            raise ResourceNotFoundError("Note introuvable.")
        if note.user_id != user_id:
            raise ForbiddenError("Accès interdit à cette note.")
        return note

    def create_note(self, user_id: int, data: NoteCreate) -> NoteResponse:
        if data.binder_id is not None:
            binder = self._binder_dao.get_by_id(data.binder_id)
            if not binder or binder.user_id != user_id:
                raise ForbiddenError("Accès interdit à ce classeur.")
                
        note = Note(
            title=data.title,
            content=data.content,
            user_id=user_id,
            binder_id=data.binder_id
        )
        created = self._note_dao.create(note)
        return NoteResponse.model_validate(created)

    def get_notes(
        self, 
        user_id: int, 
        binder_id: Optional[int] = None, 
        search: Optional[str] = None, 
        page: int = 1, 
        per_page: int = 20
    ) -> Tuple[List[NoteResponse], int]:
        offset = (page - 1) * per_page
        notes = self._note_dao.search_notes(user_id, binder_id, search, limit=per_page, offset=offset)
        total = self._note_dao.count_notes(user_id, binder_id, search)
        
        return [NoteResponse.model_validate(n) for n in notes], total

    def get_note(self, user_id: int, note_id: int) -> NoteResponse:
        note = self._get_note_or_404(note_id, user_id)
        return NoteResponse.model_validate(note)

    def update_note(self, user_id: int, note_id: int, data: NoteUpdate) -> NoteResponse:
        note = self._get_note_or_404(note_id, user_id)
        
        if data.title is not None:
            note.title = data.title
            
        if data.content is not None:
            note.content = data.content
            
        if data.binder_id is not None:
            binder = self._binder_dao.get_by_id(data.binder_id)
            if not binder or binder.user_id != user_id:
                raise ForbiddenError("Accès interdit à ce classeur.")
            note.binder_id = data.binder_id
        elif "binder_id" in data.model_fields_set and data.binder_id is None:
            note.binder_id = None
            
        updated = self._note_dao.update(note)
        return NoteResponse.model_validate(updated)

    def delete_note(self, user_id: int, note_id: int) -> None:
        note = self._get_note_or_404(note_id, user_id)
        self._note_dao.delete(note)
