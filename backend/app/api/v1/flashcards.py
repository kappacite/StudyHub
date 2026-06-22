from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.extensions import db, limiter
from app.dao.flashcard_dao import FlashcardDAO
from app.dao.deck_dao import DeckDAO
from app.dao.note_dao import NoteDAO
from app.dao.binder_dao import BinderDAO
from app.services.flashcard_service import FlashcardService
from app.services.ai_service import AIService
from app.services.flashcard_generation_service import FlashcardGenerationService
from app.schemas.flashcard_schema import FlashcardCreate, FlashcardUpdate
from app.middlewares.auth_middleware import jwt_required_middleware
import math

flashcards_bp = Blueprint("flashcards", __name__)

flashcard_dao = FlashcardDAO(db.session)
deck_dao = DeckDAO(db.session)
note_dao = NoteDAO(db.session)
binder_dao = BinderDAO(db.session)
flashcard_service = FlashcardService(flashcard_dao, deck_dao)
flashcard_generation_service = FlashcardGenerationService(note_dao, binder_dao, AIService())


def _gen_rate_limit_key():
    try:
        identity = get_jwt_identity()
        if identity:
            return str(identity)
    except Exception:
        pass
    from flask_limiter.util import get_remote_address
    return get_remote_address()

@flashcards_bp.route("", methods=["GET"])
@jwt_required_middleware
def get_flashcards(deck_id):
    user_id = int(get_jwt_identity())
    
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    
    cards, total = flashcard_service.get_flashcards(user_id, deck_id, page, per_page)
    pages = math.ceil(total / per_page) if total > 0 else 0
    
    return jsonify({
        "data": [c.model_dump() for c in cards],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": pages
        }
    }), 200

@flashcards_bp.route("", methods=["POST"])
@jwt_required_middleware
def create_flashcard(deck_id):
    user_id = int(get_jwt_identity())
    data_dict = request.get_json() or {}
    
    card_create = FlashcardCreate.model_validate(data_dict)
    
    result = flashcard_service.create_flashcard(user_id, deck_id, card_create)
    return jsonify(result.model_dump()), 201

@flashcards_bp.route("/<int:card_id>", methods=["GET"])
@jwt_required_middleware
def get_flashcard(deck_id, card_id):
    user_id = int(get_jwt_identity())
    result = flashcard_service.get_flashcard(user_id, deck_id, card_id)
    return jsonify(result.model_dump()), 200

@flashcards_bp.route("/<int:card_id>", methods=["PUT"])
@jwt_required_middleware
def update_flashcard(deck_id, card_id):
    user_id = int(get_jwt_identity())
    data_dict = request.get_json() or {}
    
    card_update = FlashcardUpdate.model_validate(data_dict)
    
    result = flashcard_service.update_flashcard(user_id, deck_id, card_id, card_update)
    return jsonify(result.model_dump()), 200

@flashcards_bp.route("/<int:card_id>", methods=["DELETE"])
@jwt_required_middleware
def delete_flashcard(deck_id, card_id):
    user_id = int(get_jwt_identity())
    flashcard_service.delete_flashcard(user_id, deck_id, card_id)
    return "", 204

@flashcards_bp.route("/<int:card_id>/history", methods=["GET"])
@jwt_required_middleware
def get_flashcard_history(deck_id, card_id):
    user_id = int(get_jwt_identity())
    entries = flashcard_service.get_history(user_id, deck_id, card_id)
    return jsonify({"data": [e.model_dump(mode="json") for e in entries]}), 200

# --- API globale de révision directe sans deck_id ---
flashcards_global_bp = Blueprint("flashcards_global", __name__)


@flashcards_global_bp.route("/generate", methods=["POST"])
@jwt_required_middleware
@limiter.limit("20 per hour", key_func=_gen_rate_limit_key)
def generate_flashcards():
    """Génère des flashcards par IA depuis une note ou un classeur.

    Ne crée pas les cartes : renvoie une liste {front, back} que le client
    insère ensuite via les endpoints de création (avec dédoublonnage).
    """
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    source_type = data.get("source_type")
    source_id = data.get("note_id") if source_type == "note" else data.get("binder_id")

    try:
        cards = flashcard_generation_service.generate_from_source(user_id, source_type, source_id)
    except RuntimeError as e:
        # Erreur côté fournisseur IA (clé absente, réseau, réponse invalide…)
        return jsonify({
            "error": {
                "code": "AI_GENERATION_FAILED",
                "message": str(e),
                "details": {}
            }
        }), 502

    return jsonify({"flashcards": cards, "count": len(cards)}), 200


@flashcards_global_bp.route("/<int:card_id>/review", methods=["PATCH"])
@jwt_required_middleware
def review_card(card_id):
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    score = data.get("score")
    if score is None or not isinstance(score, int) or not (0 <= score <= 5):
        return jsonify({
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Le score de révision est obligatoire et doit être un entier entre 0 et 5."
            }
        }), 400
        
    result = flashcard_service.review_card(user_id, card_id, score)
    return jsonify(result.model_dump()), 200
