from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.extensions import db
from app.dao.note_dao import NoteDAO
from app.dao.binder_dao import BinderDAO
from app.dao.deck_dao import DeckDAO
from app.dao.flashcard_dao import FlashcardDAO
from app.services.note_service import NoteService
from app.schemas.note_schema import NoteCreate, NoteUpdate
from app.middlewares.auth_middleware import jwt_required_middleware
from app.api.v1.tags import remove_entity_tag, set_entity_tags
import math

notes_bp = Blueprint("notes", __name__)

note_dao = NoteDAO(db.session)
binder_dao = BinderDAO(db.session)
deck_dao = DeckDAO(db.session)
flashcard_dao = FlashcardDAO(db.session)
note_service = NoteService(note_dao, binder_dao, deck_dao, flashcard_dao)

@notes_bp.route("", methods=["GET"])
@jwt_required_middleware
def get_notes():
    user_id = int(get_jwt_identity())
    
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    
    binder_id_str = request.args.get("binder_id")
    binder_id = int(binder_id_str) if binder_id_str is not None and binder_id_str != "" else None
    
    search = request.args.get("search")
    tag_id = request.args.get("tag_id", type=int)
    
    notes, total = note_service.get_notes(user_id, binder_id, search, tag_id, page, per_page)
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


@notes_bp.route("/<int:note_id>/tags", methods=["POST"])
@jwt_required_middleware
def set_note_tags(note_id):
    return set_entity_tags("notes", note_id)


@notes_bp.route("/<int:note_id>/tags/<int:tag_id>", methods=["DELETE"])
@jwt_required_middleware
def remove_note_tag(note_id, tag_id):
    return remove_entity_tag("notes", note_id, tag_id)


# -------------------------------------------------------
# Endpoints PUBLICS (sans JWT)
# -------------------------------------------------------

@notes_bp.route("/public/<string:token>", methods=["GET"])
def get_public_note(token):
    """Accès public à une note via son share_token."""
    from app.models.note import Note
    from app.extensions import db as _db
    note = _db.session.query(Note).filter_by(share_token=token, is_public=True).first()
    if not note:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Note introuvable ou non publique."}}), 404
        
    # Négociation de contenu Markdown pour les agents
    if "text/markdown" in request.headers.get("Accept", ""):
        from flask import make_response
        content = f"# {note.title}\n\n{note.content}"
        response = make_response(content)
        response.headers["Content-Type"] = "text/markdown; charset=utf-8"
        response.headers["x-markdown-tokens"] = str(len(content) // 4)
        return response

    from app.schemas.note_schema import NoteResponse
    return jsonify(NoteResponse.model_validate(note).model_dump()), 200


# -------------------------------------------------------
# Toggle visibilité
# -------------------------------------------------------

@notes_bp.route("/<int:note_id>/visibility", methods=["PATCH"])
@jwt_required_middleware
def toggle_note_visibility(note_id):
    """Passe une note en public ou privé et retourne le lien de partage."""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    is_public = data.get("is_public")
    if is_public is None:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": "Champ is_public requis."}}), 400

    from app.schemas.note_schema import NoteUpdate
    note_update = NoteUpdate(is_public=is_public)
    result = note_service.update_note(user_id, note_id, note_update)
    return jsonify(result.model_dump()), 200
