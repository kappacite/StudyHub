from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.extensions import db
from app.dao.diagram_dao import DiagramDAO
from app.dao.binder_dao import BinderDAO
from app.services.diagram_service import DiagramService
from app.schemas.diagram_schema import DiagramCreate, DiagramUpdate
from app.middlewares.auth_middleware import jwt_required_middleware
import math

diagrams_bp = Blueprint("diagrams", __name__)

diagram_dao = DiagramDAO(db.session)
binder_dao = BinderDAO(db.session)
diagram_service = DiagramService(diagram_dao, binder_dao)

@diagrams_bp.route("", methods=["GET"])
@jwt_required_middleware
def get_diagrams():
    user_id = int(get_jwt_identity())
    
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    
    binder_id_str = request.args.get("binder_id")
    binder_id = int(binder_id_str) if binder_id_str is not None and binder_id_str != "" else None
    
    diagrams, total = diagram_service.get_diagrams(user_id, binder_id, page, per_page)
    pages = math.ceil(total / per_page) if total > 0 else 0
    
    return jsonify({
        "data": [d.model_dump() for d in diagrams],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": pages
        }
    }), 200

@diagrams_bp.route("", methods=["POST"])
@jwt_required_middleware
def create_diagram():
    user_id = int(get_jwt_identity())
    data_dict = request.get_json() or {}
    
    diagram_create = DiagramCreate.model_validate(data_dict)
    
    result = diagram_service.create_diagram(user_id, diagram_create)
    return jsonify(result.model_dump()), 201

@diagrams_bp.route("/<int:diagram_id>", methods=["GET"])
@jwt_required_middleware
def get_diagram(diagram_id):
    user_id = int(get_jwt_identity())
    result = diagram_service.get_diagram(user_id, diagram_id)
    return jsonify(result.model_dump()), 200

@diagrams_bp.route("/<int:diagram_id>", methods=["PUT"])
@jwt_required_middleware
def update_diagram(diagram_id):
    user_id = int(get_jwt_identity())
    data_dict = request.get_json() or {}
    
    diagram_update = DiagramUpdate.model_validate(data_dict)
    
    result = diagram_service.update_diagram(user_id, diagram_id, diagram_update)
    return jsonify(result.model_dump()), 200

@diagrams_bp.route("/<int:diagram_id>", methods=["DELETE"])
@jwt_required_middleware
def delete_diagram(diagram_id):
    user_id = int(get_jwt_identity())
    diagram_service.delete_diagram(user_id, diagram_id)
    return "", 204
