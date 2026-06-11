from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity
from app.dao.tag_dao import TagDAO
from app.extensions import db
from app.middlewares.auth_middleware import jwt_required_middleware
from app.schemas.tag_schema import TagCreateSchema, TagSetSchema, TagUpdateSchema
from app.services.tag_service import TagService

tags_bp = Blueprint("tags", __name__)

tag_dao = TagDAO(db.session)
tag_service = TagService(tag_dao)


@tags_bp.route("", methods=["GET"])
@jwt_required_middleware
def get_tags():
    user_id = int(get_jwt_identity())
    tags = tag_service.list_tags(user_id)
    return jsonify({"data": [tag.model_dump() for tag in tags]}), 200


@tags_bp.route("", methods=["POST"])
@jwt_required_middleware
def create_tag():
    user_id = int(get_jwt_identity())
    data = TagCreateSchema.model_validate(request.get_json() or {})
    tag = tag_service.create_tag(user_id, data)
    return jsonify(tag.model_dump()), 201


@tags_bp.route("/<int:tag_id>", methods=["PUT"])
@jwt_required_middleware
def update_tag(tag_id):
    user_id = int(get_jwt_identity())
    data = TagUpdateSchema.model_validate(request.get_json() or {})
    tag = tag_service.update_tag(user_id, tag_id, data)
    return jsonify(tag.model_dump()), 200


@tags_bp.route("/<int:tag_id>", methods=["DELETE"])
@jwt_required_middleware
def delete_tag(tag_id):
    user_id = int(get_jwt_identity())
    tag_service.delete_tag(user_id, tag_id)
    return "", 204


def set_entity_tags(entity_type: str, entity_id: int):
    user_id = int(get_jwt_identity())
    data = TagSetSchema.model_validate(request.get_json() or {})
    tags = tag_service.set_tags_for_entity(user_id, entity_type, entity_id, data.tag_ids)
    return jsonify({"data": [tag.model_dump() for tag in tags]}), 200


def remove_entity_tag(entity_type: str, entity_id: int, tag_id: int):
    user_id = int(get_jwt_identity())
    tag_service.remove_tag_from_entity(user_id, entity_type, entity_id, tag_id)
    return "", 204
