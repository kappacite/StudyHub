from typing import List, Tuple, Optional
from app.dao.binder_dao import BinderDAO
from app.dao.tag_dao import TagDAO
from app.models.binder import Binder
from app.schemas.tag_schema import TagCreateSchema
from app.schemas.binder_schema import BinderCreate, BinderUpdate, BinderResponse
from app.services.tag_service import TagService
from app.middlewares.error_handler import ResourceNotFoundError, ForbiddenError, ValidationError

class BinderService:
    def __init__(self, binder_dao: BinderDAO):
        self._binder_dao = binder_dao
        self._tag_service = TagService(TagDAO(binder_dao.db))

    def _get_binder_or_404(self, binder_id, user_id: int, write_required: bool = False) -> Binder:
        from app.utils.security import check_binder_access
        return check_binder_access(self._binder_dao.db, binder_id, user_id, write_required)

    def create_binder(self, user_id: int, data: BinderCreate) -> BinderResponse:
        parent_id_internal = None
        # Si un parent_id est spécifié, vérifier son existence et son appartenance
        if data.parent_id is not None:
            parent_binder = self._get_binder_or_404(data.parent_id, user_id, write_required=True)
            parent_id_internal = parent_binder._id
            
        binder = Binder(
            name=data.name,
            user_id=user_id,
            parent_id=parent_id_internal,
            is_public=data.is_public or False,
            description=data.description,
        )
        if data.tags:
            binder.tags = self._get_or_create_tags(user_id, data.tags)
        created = self._binder_dao.create(binder)
        return BinderResponse.model_validate(created)

    def get_binder(self, user_id: int, binder_id) -> BinderResponse:
        binder = self._get_binder_or_404(binder_id, user_id, write_required=False)
        return BinderResponse.model_validate(binder)

    def get_binders(
        self,
        user_id: int,
        parent_id,
        tag_id: Optional[int] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> Tuple[List[BinderResponse], int]:
        offset = (page - 1) * per_page
        binders = self._binder_dao.get_by_parent(user_id, parent_id, tag_id, limit=per_page, offset=offset)
        total = self._binder_dao.count_by_parent(user_id, parent_id, tag_id)
        
        return [BinderResponse.model_validate(b) for b in binders], total

    def update_binder(self, user_id: int, binder_id, data: BinderUpdate) -> BinderResponse:
        binder = self._get_binder_or_404(binder_id, user_id, write_required=True)
        
        if data.name is not None:
            binder.name = data.name
            
        if data.parent_id is not None:
            if data.parent_id == binder_id:
                raise ValidationError("Un classeur ne peut pas être son propre parent.")
            parent_binder = self._get_binder_or_404(data.parent_id, user_id, write_required=True)
            binder.parent_id = parent_binder._id
        elif "parent_id" in data.model_fields_set and data.parent_id is None:
            binder.parent_id = None
            
        if data.is_public is not None:
            binder.is_public = data.is_public
        if data.description is not None:
            binder.description = data.description
        if data.tags is not None:
            binder.tags = self._get_or_create_tags(user_id, data.tags)
        updated = self._binder_dao.update(binder)
        return BinderResponse.model_validate(updated)

    def delete_binder(self, user_id: int, binder_id) -> None:
        binder = self._get_binder_or_404(binder_id, user_id, write_required=True)
        self._binder_dao.delete(binder)

    def get_all_binders_flat(self, user_id: int) -> List[BinderResponse]:
        binders = self._binder_dao.get_all(user_id, limit=1000)
        responses = [BinderResponse.model_validate(b) for b in binders]
        seen = {r.id for r in responses}

        # Classeurs partagés par un cours/groupe : on ajoute le sous-arbre en lecture
        # seule. La racine partagée est détachée (parent_id=None) pour apparaître à la
        # racine de l'arbre de l'élève ; les descendants gardent leur parent.
        for root in self._binder_dao.get_shared_root_binders(user_id):
            subtree = [(root, True)] + [(d, False) for d in self._binder_dao.get_descendants(root._id)]
            for binder, is_root in subtree:
                if binder.id in seen:
                    continue
                resp = BinderResponse.model_validate(binder)
                resp.read_only = True
                if is_root:
                    resp.parent_id = None
                responses.append(resp)
                seen.add(binder.id)
        return responses

    def _get_or_create_tags(self, user_id: int, names: List[str]):
        tags = []
        seen = set()
        tag_dao = self._tag_service._tag_dao
        for raw_name in names:
            name = " ".join(raw_name.strip().split())
            if not name or name.lower() in seen:
                continue
            seen.add(name.lower())
            tag = tag_dao.get_by_name(user_id, name)
            if not tag:
                tag = self._tag_service.create_tag(user_id, TagCreateSchema(name=name, color=None))
                tag = tag_dao.get_by_id(tag.id)
            tags.append(tag)
        return tags
