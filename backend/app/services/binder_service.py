from typing import List, Tuple, Optional
from app.dao.binder_dao import BinderDAO
from app.models.binder import Binder
from app.schemas.binder_schema import BinderCreate, BinderUpdate, BinderResponse
from app.middlewares.error_handler import ResourceNotFoundError, ForbiddenError, ValidationError

class BinderService:
    def __init__(self, binder_dao: BinderDAO):
        self._binder_dao = binder_dao

    def _get_binder_or_404(self, binder_id: int, user_id: int) -> Binder:
        binder = self._binder_dao.get_by_id(binder_id)
        if not binder:
            raise ResourceNotFoundError("Classeur introuvable.")
        if binder.user_id != user_id:
            raise ForbiddenError("Accès interdit à ce classeur.")
        return binder

    def create_binder(self, user_id: int, data: BinderCreate) -> BinderResponse:
        # Si un parent_id est spécifié, vérifier son existence et son appartenance
        if data.parent_id is not None:
            self._get_binder_or_404(data.parent_id, user_id)
            
        binder = Binder(
            name=data.name,
            user_id=user_id,
            parent_id=data.parent_id
        )
        created = self._binder_dao.create(binder)
        return BinderResponse.model_validate(created)

    def get_binder(self, user_id: int, binder_id: int) -> BinderResponse:
        binder = self._get_binder_or_404(binder_id, user_id)
        return BinderResponse.model_validate(binder)

    def get_binders(self, user_id: int, parent_id: Optional[int], page: int = 1, per_page: int = 20) -> Tuple[List[BinderResponse], int]:
        offset = (page - 1) * per_page
        binders = self._binder_dao.get_by_parent(user_id, parent_id, limit=per_page, offset=offset)
        total = self._binder_dao.count_by_parent(user_id, parent_id)
        
        return [BinderResponse.model_validate(b) for b in binders], total

    def update_binder(self, user_id: int, binder_id: int, data: BinderUpdate) -> BinderResponse:
        binder = self._get_binder_or_404(binder_id, user_id)
        
        if data.name is not None:
            binder.name = data.name
            
        if data.parent_id is not None:
            if data.parent_id == binder_id:
                raise ValidationError("Un classeur ne peut pas être son propre parent.")
            # Vérifier que le parent existe et appartient bien à l'utilisateur
            self._get_binder_or_404(data.parent_id, user_id)
            
            # TODO : Idéalement, vérifier qu'on ne crée pas de cycle récursif.
            # Pour l'instant, on affecte le parent_id.
            binder.parent_id = data.parent_id
        elif "parent_id" in data.model_fields_set and data.parent_id is None:
            binder.parent_id = None
            
        updated = self._binder_dao.update(binder)
        return BinderResponse.model_validate(updated)

    def delete_binder(self, user_id: int, binder_id: int) -> None:
        binder = self._get_binder_or_404(binder_id, user_id)
        self._binder_dao.delete(binder)
