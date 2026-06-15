from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.extensions import db
from app.dao.binder_dao import BinderDAO
from app.dao.note_dao import NoteDAO
from app.dao.deck_dao import DeckDAO
from app.dao.diagram_dao import DiagramDAO
from app.dao.pdf_dao import PDFDAO
from app.dao.revision_dao import RevisionSetDAO
from app.services.binder_service import BinderService
from app.services.binder_items_service import BinderItemsService
from app.schemas.binder_schema import BinderCreate, BinderUpdate, BinderItemsRequest
from app.middlewares.auth_middleware import jwt_required_middleware
from app.api.v1.tags import remove_entity_tag, set_entity_tags
import math

binders_bp = Blueprint("binders", __name__)

binder_dao = BinderDAO(db.session)
binder_service = BinderService(binder_dao)
binder_items_service = BinderItemsService(
    binder_dao, NoteDAO(db.session), DeckDAO(db.session),
    RevisionSetDAO(db.session), DiagramDAO(db.session), PDFDAO(db.session),
)

@binders_bp.route("", methods=["GET"])
@jwt_required_middleware
def get_binders():
    user_id = int(get_jwt_identity())
    
    # Check if all binders are requested
    all_binders = request.args.get("all", "false").lower() == "true"
    if all_binders:
        binders = binder_service.get_all_binders_flat(user_id)
        return jsonify({
            "data": [b.model_dump() for b in binders]
        }), 200

    # Query parameters
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    
    parent_id = request.args.get("parent_id")
    if parent_id == "":
        parent_id = None
    tag_id = request.args.get("tag_id", type=int)
    
    # Appel service
    binders, total = binder_service.get_binders(user_id, parent_id, tag_id, page, per_page)
    
    pages = math.ceil(total / per_page) if total > 0 else 0
    
    return jsonify({
        "data": [b.model_dump() for b in binders],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": pages
        }
    }), 200

@binders_bp.route("", methods=["POST"])
@jwt_required_middleware
def create_binder():
    user_id = int(get_jwt_identity())
    data_dict = request.get_json() or {}
    
    binder_create = BinderCreate.model_validate(data_dict)
    
    result = binder_service.create_binder(user_id, binder_create)
    return jsonify(result.model_dump()), 201

@binders_bp.route("/<binder_id>", methods=["GET"])
@jwt_required_middleware
def get_binder(binder_id):
    user_id = int(get_jwt_identity())
    result = binder_service.get_binder(user_id, binder_id)
    return jsonify(result.model_dump()), 200

@binders_bp.route("/<binder_id>", methods=["PUT"])
@jwt_required_middleware
def update_binder(binder_id):
    user_id = int(get_jwt_identity())
    data_dict = request.get_json() or {}
    
    # On autorise des champs manquants car c'est un PUT partiel (ou PATCH)
    binder_update = BinderUpdate.model_validate(data_dict)
    
    result = binder_service.update_binder(user_id, binder_id, binder_update)
    return jsonify(result.model_dump()), 200

@binders_bp.route("/<binder_id>", methods=["DELETE"])
@jwt_required_middleware
def delete_binder(binder_id):
    user_id = int(get_jwt_identity())
    binder_service.delete_binder(user_id, binder_id)
    return "", 204


@binders_bp.route("/<binder_id>/items", methods=["POST"])
@jwt_required_middleware
def attach_binder_items(binder_id):
    user_id = int(get_jwt_identity())
    payload = BinderItemsRequest.model_validate(request.get_json() or {})
    attached = binder_items_service.attach(user_id, binder_id, payload.items)
    return jsonify({"attached": attached}), 200

@binders_bp.route("/<binder_id>/items/detach", methods=["POST"])
@jwt_required_middleware
def detach_binder_items(binder_id):
    user_id = int(get_jwt_identity())
    payload = BinderItemsRequest.model_validate(request.get_json() or {})
    detached = binder_items_service.detach(user_id, payload.items)
    return jsonify({"detached": detached}), 200


@binders_bp.route("/<binder_id>/tags", methods=["POST"])
@jwt_required_middleware
def set_binder_tags(binder_id):
    return set_entity_tags("binders", binder_id)


@binders_bp.route("/<binder_id>/tags/<int:tag_id>", methods=["DELETE"])
@jwt_required_middleware
def remove_binder_tag(binder_id, tag_id):
    return remove_entity_tag("binders", binder_id, tag_id)


# -------------------------------------------------------
# Endpoints PUBLICS (sans JWT)
# -------------------------------------------------------

@binders_bp.route("/public/<binder_id>", methods=["GET"])
def get_public_package_binder(binder_id):
    """Accès public à un classeur (is_public=True)."""
    from app.models.binder import Binder
    from app.extensions import db as _db
    binder = _db.session.query(Binder).filter_by(id=str(binder_id), is_public=True).first()
    if not binder:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Classeur introuvable ou non public."}}), 404
    from app.schemas.binder_schema import BinderResponse
    return jsonify(BinderResponse.model_validate(binder).model_dump()), 200


# -------------------------------------------------------
# Toggle visibilité
# -------------------------------------------------------

@binders_bp.route("/<binder_id>/visibility", methods=["PATCH"])
@jwt_required_middleware
def toggle_binder_visibility(binder_id):
    """Passe un classeur en public ou privé."""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    is_public = data.get("is_public")
    if is_public is None:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": "Champ is_public requis."}}), 400

    from app.schemas.binder_schema import BinderUpdate
    binder_update = BinderUpdate(is_public=is_public)
    result = binder_service.update_binder(user_id, binder_id, binder_update)
    return jsonify(result.model_dump()), 200
