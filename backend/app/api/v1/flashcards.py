from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.extensions import db
from app.dao.flashcard_dao import FlashcardDAO
from app.dao.deck_dao import DeckDAO
from app.services.flashcard_service import FlashcardService
from app.schemas.flashcard_schema import FlashcardCreate, FlashcardUpdate
from app.middlewares.auth_middleware import jwt_required_middleware
import math

flashcards_bp = Blueprint("flashcards", __name__)

flashcard_dao = FlashcardDAO(db.session)
deck_dao = DeckDAO(db.session)
flashcard_service = FlashcardService(flashcard_dao, deck_dao)

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
