from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.extensions import db
from app.dao.deck_dao import DeckDAO
from app.dao.binder_dao import BinderDAO
from app.dao.flashcard_dao import FlashcardDAO
from app.services.deck_service import DeckService
from app.services.flashcard_service import FlashcardService
from app.schemas.deck_schema import DeckCreate, DeckUpdate
from app.schemas.flashcard_schema import FlashcardAnswer
from app.middlewares.auth_middleware import jwt_required_middleware
import math

decks_bp = Blueprint("decks", __name__)

deck_dao = DeckDAO(db.session)
binder_dao = BinderDAO(db.session)
flashcard_dao = FlashcardDAO(db.session)

deck_service = DeckService(deck_dao, binder_dao)
flashcard_service = FlashcardService(flashcard_dao, deck_dao)

@decks_bp.route("", methods=["GET"])
@jwt_required_middleware
def get_decks():
    user_id = int(get_jwt_identity())
    
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    
    binder_id_str = request.args.get("binder_id")
    binder_id = int(binder_id_str) if binder_id_str is not None and binder_id_str != "" else None
    
    search = request.args.get("search")
    
    decks, total = deck_service.get_decks(user_id, binder_id, search, page, per_page)
    pages = math.ceil(total / per_page) if total > 0 else 0
    
    return jsonify({
        "data": [d.model_dump() for d in decks],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": pages
        }
    }), 200

@decks_bp.route("", methods=["POST"])
@jwt_required_middleware
def create_deck():
    user_id = int(get_jwt_identity())
    data_dict = request.get_json() or {}
    
    deck_create = DeckCreate.model_validate(data_dict)
    
    result = deck_service.create_deck(user_id, deck_create)
    return jsonify(result.model_dump()), 201

@decks_bp.route("/<int:deck_id>", methods=["GET"])
@jwt_required_middleware
def get_deck(deck_id):
    user_id = int(get_jwt_identity())
    result = deck_service.get_deck(user_id, deck_id)
    return jsonify(result.model_dump()), 200

@decks_bp.route("/<int:deck_id>", methods=["PUT"])
@jwt_required_middleware
def update_deck(deck_id):
    user_id = int(get_jwt_identity())
    data_dict = request.get_json() or {}
    
    deck_update = DeckUpdate.model_validate(data_dict)
    
    result = deck_service.update_deck(user_id, deck_id, deck_update)
    return jsonify(result.model_dump()), 200

@decks_bp.route("/<int:deck_id>", methods=["DELETE"])
@jwt_required_middleware
def delete_deck(deck_id):
    user_id = int(get_jwt_identity())
    deck_service.delete_deck(user_id, deck_id)
    return "", 204

# --- Endpoints de révision SM-2 ---

@decks_bp.route("/<int:deck_id>/study", methods=["GET"])
@jwt_required_middleware
def get_study(deck_id):
    user_id = int(get_jwt_identity())
    cards = flashcard_service.get_study_cards(user_id, deck_id)
    return jsonify([c.model_dump() for c in cards]), 200

@decks_bp.route("/<int:deck_id>/study/answer/<int:card_id>", methods=["POST"])
@jwt_required_middleware
def answer_card(deck_id, card_id):
    user_id = int(get_jwt_identity())
    data_dict = request.get_json() or {}
    
    # Validation du score
    answer = FlashcardAnswer.model_validate(data_dict)
    
    result = flashcard_service.answer_card(user_id, deck_id, card_id, answer.score)
    return jsonify(result.model_dump()), 200
