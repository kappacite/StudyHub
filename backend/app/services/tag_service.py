import re
from typing import List
from sqlalchemy.exc import IntegrityError
from app.dao.tag_dao import ENTITY_MODELS, TagDAO
from app.models.tag import Tag
from app.schemas.tag_schema import TagCreateSchema, TagResponseSchema, TagUpdateSchema
from app.middlewares.error_handler import ConflictError, ForbiddenError, ResourceNotFoundError, ValidationError


HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
MAX_TAGS_PER_USER = 50


class TagService:
    def __init__(self, tag_dao: TagDAO):
        self._tag_dao = tag_dao

    def list_tags(self, user_id: int) -> List[TagResponseSchema]:
        tags = self._tag_dao.get_by_user(user_id)
        return [TagResponseSchema.model_validate(tag) for tag in tags]

    def create_tag(self, user_id: int, data: TagCreateSchema) -> TagResponseSchema:
        name = self._normalize_name(data.name)
        self._validate_color(data.color)

        if self._tag_dao.count_by_user(user_id) >= MAX_TAGS_PER_USER:
            raise ValidationError("Limite de 50 tags atteinte.")
        if self._tag_dao.get_by_name(user_id, name):
            raise ConflictError("Un tag avec ce nom existe déjà.")

        tag = Tag(name=name, color=data.color, user_id=user_id)
        try:
            created = self._tag_dao.create(tag)
        except IntegrityError:
            self._tag_dao.db.rollback()
            raise ConflictError("Un tag avec ce nom existe déjà.")
        return TagResponseSchema.model_validate(created)

    def update_tag(self, user_id: int, tag_id: int, data: TagUpdateSchema) -> TagResponseSchema:
        tag = self._get_tag_or_404(tag_id, user_id)

        if data.name is not None:
            name = self._normalize_name(data.name)
            existing = self._tag_dao.get_by_name(user_id, name)
            if existing and existing.id != tag_id:
                raise ConflictError("Un tag avec ce nom existe déjà.")
            tag.name = name

        if "color" in data.model_fields_set:
            self._validate_color(data.color)
            tag.color = data.color

        try:
            updated = self._tag_dao.update(tag)
        except IntegrityError:
            self._tag_dao.db.rollback()
            raise ConflictError("Un tag avec ce nom existe déjà.")
        return TagResponseSchema.model_validate(updated)

    def delete_tag(self, user_id: int, tag_id: int) -> None:
        tag = self._get_tag_or_404(tag_id, user_id)
        self._tag_dao.delete(tag)

    def set_tags_for_entity(
        self,
        user_id: int,
        entity_type: str,
        entity_id: int,
        tag_ids: list[int],
    ) -> List[TagResponseSchema]:
        entity = self._get_owned_entity_or_404(user_id, entity_type, entity_id)
        unique_tag_ids = list(dict.fromkeys(tag_ids))
        tags = self._tag_dao.get_owned_tags(user_id, unique_tag_ids)

        if len(tags) != len(unique_tag_ids):
            raise ForbiddenError("Un ou plusieurs tags ne vous appartiennent pas.")

        entity.tags = tags
        self._tag_dao.db.commit()
        self._tag_dao.db.refresh(entity)
        return [TagResponseSchema.model_validate(tag) for tag in entity.tags]

    def remove_tag_from_entity(self, user_id: int, entity_type: str, entity_id: int, tag_id: int) -> None:
        entity = self._get_owned_entity_or_404(user_id, entity_type, entity_id)
        tag = self._get_tag_or_404(tag_id, user_id)
        if tag in entity.tags:
            entity.tags.remove(tag)
            self._tag_dao.db.commit()

    def _get_tag_or_404(self, tag_id: int, user_id: int) -> Tag:
        tag = self._tag_dao.get_by_id(tag_id)
        if not tag:
            raise ResourceNotFoundError("Tag introuvable.")
        if tag.user_id != user_id:
            raise ForbiddenError("Accès interdit à ce tag.")
        return tag

    def _get_owned_entity_or_404(self, user_id: int, entity_type: str, entity_id: int):
        if entity_type not in ENTITY_MODELS:
            raise ResourceNotFoundError("Type de ressource introuvable.")
        entity = self._tag_dao.get_entity(entity_type, entity_id)
        if not entity:
            raise ResourceNotFoundError("Ressource introuvable.")
        if entity.user_id != user_id:
            raise ForbiddenError("Accès interdit à cette ressource.")
        return entity

    def _normalize_name(self, name: str) -> str:
        normalized = " ".join(name.strip().split())
        if not normalized:
            raise ValidationError("Le nom du tag est requis.")
        if len(normalized) > 30:
            raise ValidationError("Le nom du tag ne peut pas dépasser 30 caractères.")
        return normalized

    def _validate_color(self, color: str | None) -> None:
        if color is not None and not HEX_COLOR_RE.match(color):
            raise ValidationError("La couleur doit être au format hexadécimal #RRGGBB.")
