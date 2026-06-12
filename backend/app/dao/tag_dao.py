from typing import List, Optional, Type
from sqlalchemy.orm import Session
from app.dao.base_dao import BaseDAO
from app.models.binder import Binder
from app.models.deck import Deck
from app.models.diagram import Diagram
from app.models.note import Note
from app.models.pdf_document import PDFDocument
from app.models.tag import Tag


ENTITY_MODELS: dict[str, Type] = {
    "notes": Note,
    "decks": Deck,
    "diagrams": Diagram,
    "pdfs": PDFDocument,
    "binders": Binder,
}


class TagDAO(BaseDAO[Tag]):
    def __init__(self, db: Session):
        super().__init__(Tag, db)

    def get_by_user(self, user_id: int) -> List[Tag]:
        return (
            self.db.query(self.model)
            .filter_by(user_id=user_id)
            .order_by(self.model.name.asc())
            .all()
        )

    def get_by_name(self, user_id: int, name: str) -> Optional[Tag]:
        return self.db.query(self.model).filter_by(user_id=user_id, name=name).first()

    def count_by_user(self, user_id: int) -> int:
        return self.db.query(self.model).filter_by(user_id=user_id).count()

    def get_owned_tags(self, user_id: int, tag_ids: list[int]) -> List[Tag]:
        if not tag_ids:
            return []
        return (
            self.db.query(self.model)
            .filter(self.model.user_id == user_id, self.model.id.in_(tag_ids))
            .all()
        )

    def get_entity(self, entity_type: str, entity_id):
        model = ENTITY_MODELS.get(entity_type)
        if model is None:
            return None
        if isinstance(entity_id, str):
            return self.db.query(model).filter_by(id=entity_id).first()
        return self.db.get(model, entity_id)

    def get_tags_for_entity(self, entity_type: str, entity_id: int) -> List[Tag]:
        entity = self.get_entity(entity_type, entity_id)
        return list(entity.tags) if entity else []

    def set_tags_for_entity(self, entity_type: str, entity_id: int, tags: List[Tag]):
        entity = self.get_entity(entity_type, entity_id)
        if entity is None:
            return None
        entity.tags = tags
        self.db.commit()
        self.db.refresh(entity)
        return entity
