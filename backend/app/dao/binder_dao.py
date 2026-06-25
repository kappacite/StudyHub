from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.binder import Binder
from app.dao.base_dao import BaseDAO

class BinderDAO(BaseDAO[Binder]):
    def __init__(self, db: Session):
        super().__init__(Binder, db)

    def get_by_id(self, entity_id) -> Optional[Binder]:
        if isinstance(entity_id, int) or (isinstance(entity_id, str) and entity_id.isdigit()):
            from sqlalchemy import or_
            return self.db.query(self.model).filter(or_(self.model._id == int(entity_id), self.model.id == str(entity_id))).first()
        return self.db.query(self.model).filter_by(id=str(entity_id)).first()

    def get_all(self, user_id: int, limit: int = 20, offset: int = 0) -> List[Binder]:
        from sqlalchemy.orm import selectinload
        return (
            self.db.query(self.model)
            .filter_by(user_id=user_id)
            .options(selectinload(self.model.tags), selectinload(self.model.parent))
            .limit(limit)
            .offset(offset)
            .all()
        )

    def get_by_parent(
        self,
        user_id: int,
        parent_id,
        tag_id: Optional[int] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Binder]:
        if parent_id is not None:
            if isinstance(parent_id, int) or (isinstance(parent_id, str) and parent_id.isdigit()):
                parent_id_internal = int(parent_id)
            else:
                parent = self.get_by_id(parent_id)
                parent_id_internal = parent._id if parent else None
        else:
            parent_id_internal = None

        from sqlalchemy.orm import selectinload
        query = self.db.query(self.model).filter_by(user_id=user_id, parent_id=parent_id_internal)
        if tag_id is not None:
            query = query.filter(self.model.tags.any(id=tag_id))
        return query.options(selectinload(self.model.tags), selectinload(self.model.parent)).limit(limit).offset(offset).all()
        
    def get_hidden_binder_ids(self, user_id: int) -> set:
        """Ids internes des classeurs (partagés) masqués par l'utilisateur."""
        from app.models.hidden_binder import HiddenBinder
        rows = self.db.query(HiddenBinder.binder_id).filter_by(user_id=user_id).all()
        return {r[0] for r in rows}

    def hide_binder(self, user_id: int, binder_internal_id: int) -> None:
        """Masque un classeur partagé dans la vue de l'utilisateur (idempotent)."""
        from app.models.hidden_binder import HiddenBinder
        existing = (
            self.db.query(HiddenBinder)
            .filter_by(user_id=user_id, binder_id=binder_internal_id)
            .first()
        )
        if not existing:
            self.db.add(HiddenBinder(user_id=user_id, binder_id=binder_internal_id))
            self.db.commit()

    def get_shared_root_binders(self, user_id: int) -> List[Binder]:
        """Classeurs partagés avec l'utilisateur via un groupe/classe (qu'il ne possède pas).
        Ce sont les racines, du point de vue de l'élève, des sous-arbres en lecture seule."""
        from app.models.group import GroupBinder, GroupMember
        from sqlalchemy.orm import selectinload
        return (
            self.db.query(self.model)
            .join(GroupBinder, GroupBinder.binder_id == self.model._id)
            .join(GroupMember, GroupMember.group_id == GroupBinder.group_id)
            .filter(GroupMember.user_id == user_id, self.model.user_id != user_id)
            .options(selectinload(self.model.tags))
            .distinct()
            .all()
        )

    def get_descendants(self, binder_internal_id: int) -> List[Binder]:
        """Tous les descendants (récursifs) d'un classeur, par parent_id."""
        from sqlalchemy.orm import selectinload
        result: List[Binder] = []
        stack = [binder_internal_id]
        while stack:
            pid = stack.pop()
            children = (
                self.db.query(self.model)
                .filter(self.model.parent_id == pid)
                .options(selectinload(self.model.tags))
                .all()
            )
            for c in children:
                result.append(c)
                stack.append(c._id)
        return result

    def count_by_parent(self, user_id: int, parent_id, tag_id: Optional[int] = None) -> int:
        if parent_id is not None:
            if isinstance(parent_id, int) or (isinstance(parent_id, str) and parent_id.isdigit()):
                parent_id_internal = int(parent_id)
            else:
                parent = self.get_by_id(parent_id)
                parent_id_internal = parent._id if parent else None
        else:
            parent_id_internal = None

        query = self.db.query(self.model).filter_by(user_id=user_id, parent_id=parent_id_internal)
        if tag_id is not None:
            query = query.filter(self.model.tags.any(id=tag_id))
        return query.count()
