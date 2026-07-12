import logging
from typing import List, Tuple, Optional
from app.dao.diagram_dao import DiagramDAO
from app.dao.binder_dao import BinderDAO
from app.models.diagram import Diagram
from app.schemas.diagram_schema import DiagramCreate, DiagramUpdate, DiagramResponse
from app.middlewares.error_handler import ResourceNotFoundError, ForbiddenError

logger = logging.getLogger(__name__)

class DiagramService:
    def __init__(self, diagram_dao: DiagramDAO, binder_dao: BinderDAO):
        self._diagram_dao = diagram_dao
        self._binder_dao = binder_dao

    def _get_diagram_or_404(self, diagram_id: int, user_id: int, write_required: bool = False) -> Diagram:
        diagram = self._diagram_dao.get_by_id(diagram_id)
        if not diagram:
            raise ResourceNotFoundError("Diagramme introuvable.")
        if diagram.user_id != user_id:
            # Diagramme d'un classeur partagé (cours) : lecture autorisée aux
            # membres ; l'écriture reste soumise à la permission du partage.
            if diagram.binder_id:
                from app.utils.security import check_binder_access
                check_binder_access(self._diagram_dao.db, diagram.binder_id, user_id, write_required=write_required)
            else:
                raise ForbiddenError("Accès interdit à ce diagramme.")
        return diagram

    def create_diagram(self, user_id: int, data: DiagramCreate) -> DiagramResponse:
        binder_id_internal = None
        if data.binder_id is not None:
            binder = self._binder_dao.get_by_id(data.binder_id)
            if not binder or binder.user_id != user_id:
                raise ForbiddenError("Accès interdit à ce classeur.")
            binder_id_internal = binder._id
                
        diagram = Diagram(
            title=data.title,
            code=data.code,
            user_id=user_id,
            binder_id=binder_id_internal
        )
        created = self._diagram_dao.create(diagram)
        return DiagramResponse.model_validate(created)

    def get_diagrams(
        self, 
        user_id: int, 
        binder_id: Optional[int] = None, 
        tag_id: Optional[int] = None,
        page: int = 1, 
        per_page: int = 20
    ) -> Tuple[List[DiagramResponse], int]:
        offset = (page - 1) * per_page
        diagrams = self._diagram_dao.get_by_binder(user_id, binder_id, tag_id, limit=per_page, offset=offset)
        total = self._diagram_dao.count_by_binder(user_id, binder_id, tag_id)

        responses = [DiagramResponse.model_validate(d) for d in diagrams]

        # Lors d'un listing global, inclure les diagrammes des classeurs partagés
        # (cours), en LECTURE SEULE — symétrique des notes/PDF/decks/ensembles.
        if binder_id is None and tag_id is None:
            shared_binder_ids: list = []
            for root in self._binder_dao.get_shared_root_binders(user_id):
                shared_binder_ids.append(root._id)
                shared_binder_ids.extend(d._id for d in self._binder_dao.get_descendants(root._id))
            if shared_binder_ids:
                for d in self._diagram_dao.get_by_binder_internal_ids(shared_binder_ids):
                    resp = DiagramResponse.model_validate(d)
                    resp.read_only = True
                    responses.append(resp)
                total = len(responses)

        return responses, total

    def get_diagram(self, user_id: int, diagram_id: int) -> DiagramResponse:
        diagram = self._get_diagram_or_404(diagram_id, user_id)
        return DiagramResponse.model_validate(diagram)

    def update_diagram(self, user_id: int, diagram_id: int, data: DiagramUpdate) -> DiagramResponse:
        diagram = self._get_diagram_or_404(diagram_id, user_id, write_required=True)

        if data.title is not None:
            diagram.title = data.title
            
        if data.code is not None:
            diagram.code = data.code
            
        if data.binder_id is not None:
            binder = self._binder_dao.get_by_id(data.binder_id)
            if not binder or binder.user_id != user_id:
                raise ForbiddenError("Accès interdit à ce classeur.")
            diagram.binder_id = binder._id
        elif "binder_id" in data.model_fields_set and data.binder_id is None:
            diagram.binder_id = None
            
        updated = self._diagram_dao.update(diagram)
        return DiagramResponse.model_validate(updated)

    def delete_diagram(self, user_id: int, diagram_id: int) -> None:
        diagram = self._get_diagram_or_404(diagram_id, user_id, write_required=True)
        self._diagram_dao.delete(diagram)
