from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.extensions import db
from app.dao.binder_dao import BinderDAO
from app.services.binder_service import BinderService
from app.schemas.binder_schema import BinderCreate, BinderUpdate
from app.middlewares.auth_middleware import jwt_required_middleware
import math

binders_bp = Blueprint("binders", __name__)

binder_dao = BinderDAO(db.session)
binder_service = BinderService(binder_dao)

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
    
    parent_id_str = request.args.get("parent_id")
    parent_id = int(parent_id_str) if parent_id_str is not None and parent_id_str != "" else None
    
    # Appel service
    binders, total = binder_service.get_binders(user_id, parent_id, page, per_page)
    
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

@binders_bp.route("/<int:binder_id>", methods=["GET"])
@jwt_required_middleware
def get_binder(binder_id):
    user_id = int(get_jwt_identity())
    result = binder_service.get_binder(user_id, binder_id)
    return jsonify(result.model_dump()), 200

@binders_bp.route("/<int:binder_id>", methods=["PUT"])
@jwt_required_middleware
def update_binder(binder_id):
    user_id = int(get_jwt_identity())
    data_dict = request.get_json() or {}
    
    # On autorise des champs manquants car c'est un PUT partiel (ou PATCH)
    binder_update = BinderUpdate.model_validate(data_dict)
    
    result = binder_service.update_binder(user_id, binder_id, binder_update)
    return jsonify(result.model_dump()), 200

@binders_bp.route("/<int:binder_id>", methods=["DELETE"])
@jwt_required_middleware
def delete_binder(binder_id):
    user_id = int(get_jwt_identity())
    binder_service.delete_binder(user_id, binder_id)
    return "", 204
