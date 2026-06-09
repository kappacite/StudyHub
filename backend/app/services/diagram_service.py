from typing import List, Tuple, Optional
from app.dao.diagram_dao import DiagramDAO
from app.dao.binder_dao import BinderDAO
from app.models.diagram import Diagram
from app.schemas.diagram_schema import DiagramCreate, DiagramUpdate, DiagramResponse
from app.middlewares.error_handler import ResourceNotFoundError, ForbiddenError

class DiagramService:
    def __init__(self, diagram_dao: DiagramDAO, binder_dao: BinderDAO):
        self._diagram_dao = diagram_dao
        self._binder_dao = binder_dao

    def _get_diagram_or_404(self, diagram_id: int, user_id: int) -> Diagram:
        diagram = self._diagram_dao.get_by_id(diagram_id)
        if not diagram:
            raise ResourceNotFoundError("Diagramme introuvable.")
        if diagram.user_id != user_id:
            raise ForbiddenError("Accès interdit à ce diagramme.")
        return diagram

    def create_diagram(self, user_id: int, data: DiagramCreate) -> DiagramResponse:
        if data.binder_id is not None:
            binder = self._binder_dao.get_by_id(data.binder_id)
            if not binder or binder.user_id != user_id:
                raise ForbiddenError("Accès interdit à ce classeur.")
                
        diagram = Diagram(
            title=data.title,
            code=data.code,
            user_id=user_id,
            binder_id=data.binder_id
        )
        created = self._diagram_dao.create(diagram)
        return DiagramResponse.model_validate(created)

    def get_diagrams(
        self, 
        user_id: int, 
        binder_id: Optional[int] = None, 
        page: int = 1, 
        per_page: int = 20
    ) -> Tuple[List[DiagramResponse], int]:
        offset = (page - 1) * per_page
        diagrams = self._diagram_dao.get_by_binder(user_id, binder_id, limit=per_page, offset=offset)
        total = self._diagram_dao.count_by_binder(user_id, binder_id)
        
        return [DiagramResponse.model_validate(d) for d in diagrams], total

    def get_diagram(self, user_id: int, diagram_id: int) -> DiagramResponse:
        diagram = self._get_diagram_or_404(diagram_id, user_id)
        return DiagramResponse.model_validate(diagram)

    def update_diagram(self, user_id: int, diagram_id: int, data: DiagramUpdate) -> DiagramResponse:
        diagram = self._get_diagram_or_404(diagram_id, user_id)
        
        if data.title is not None:
            diagram.title = data.title
            
        if data.code is not None:
            diagram.code = data.code
            
        if data.binder_id is not None:
            binder = self._binder_dao.get_by_id(data.binder_id)
            if not binder or binder.user_id != user_id:
                raise ForbiddenError("Accès interdit à ce classeur.")
            diagram.binder_id = data.binder_id
        elif "binder_id" in data.model_fields_set and data.binder_id is None:
            diagram.binder_id = None
            
        updated = self._diagram_dao.update(diagram)
        
        # --- NEW: Synchroniser les notes associées si le code a changé ---
        if data.code is not None:
            try:
                from app.models.note import Note
                from app.services.note_service import NoteService
                from app.dao.note_dao import NoteDAO
                from app.dao.deck_dao import DeckDAO
                from app.dao.flashcard_dao import FlashcardDAO
                
                note_dao = NoteDAO(self._diagram_dao.db)
                deck_dao = DeckDAO(self._diagram_dao.db)
                flashcard_dao = FlashcardDAO(self._diagram_dao.db)
                note_service = NoteService(note_dao, self._binder_dao, deck_dao, flashcard_dao)
                
                tag = f"[diagram:{diagram.id}]"
                notes = self._diagram_dao.db.query(Note).filter(Note.content.like(f"%{tag}%")).all()
                for note in notes:
                    note_service._sync_phantom_deck(note)
            except Exception as e:
                print(f"Error syncing notes on diagram update: {e}")
                
        return DiagramResponse.model_validate(updated)

    def delete_diagram(self, user_id: int, diagram_id: int) -> None:
        diagram = self._get_diagram_or_404(diagram_id, user_id)
        self._diagram_dao.delete(diagram)
