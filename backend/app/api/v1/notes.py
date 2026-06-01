from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.extensions import db
from app.dao.note_dao import NoteDAO
from app.dao.binder_dao import BinderDAO
from app.services.note_service import NoteService
from app.schemas.note_schema import NoteCreate, NoteUpdate
from app.middlewares.auth_middleware import jwt_required_middleware
import math

notes_bp = Blueprint("notes", __name__)

note_dao = NoteDAO(db.session)
binder_dao = BinderDAO(db.session)
note_service = NoteService(note_dao, binder_dao)

@notes_bp.route("", methods=["GET"])
@jwt_required_middleware
def get_notes():
    user_id = int(get_jwt_identity())
    
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    
    binder_id_str = request.args.get("binder_id")
    binder_id = int(binder_id_str) if binder_id_str is not None and binder_id_str != "" else None
    
    search = request.args.get("search")
    
    notes, total = note_service.get_notes(user_id, binder_id, search, page, per_page)
    pages = math.ceil(total / per_page) if total > 0 else 0
    
    return jsonify({
        "data": [n.model_dump() for n in notes],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": pages
        }
    }), 200

@notes_bp.route("", methods=["POST"])
@jwt_required_middleware
def create_note():
    user_id = int(get_jwt_identity())
    data_dict = request.get_json() or {}
    
    note_create = NoteCreate.model_validate(data_dict)
    
    result = note_service.create_note(user_id, note_create)
    return jsonify(result.model_dump()), 201

@notes_bp.route("/<int:note_id>", methods=["GET"])
@jwt_required_middleware
def get_note(note_id):
    user_id = int(get_jwt_identity())
    result = note_service.get_note(user_id, note_id)
    return jsonify(result.model_dump()), 200

@notes_bp.route("/<int:note_id>", methods=["PUT"])
@jwt_required_middleware
def update_note(note_id):
    user_id = int(get_jwt_identity())
    data_dict = request.get_json() or {}
    
    note_update = NoteUpdate.model_validate(data_dict)
    
    result = note_service.update_note(user_id, note_id, note_update)
    return jsonify(result.model_dump()), 200

@notes_bp.route("/<int:note_id>", methods=["DELETE"])
@jwt_required_middleware
def delete_note(note_id):
    user_id = int(get_jwt_identity())
    note_service.delete_note(user_id, note_id)
    return "", 204
