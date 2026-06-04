from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.extensions import db
from app.dao.note_dao import NoteDAO
from app.dao.deck_dao import DeckDAO
from app.dao.flashcard_dao import FlashcardDAO
from app.dao.study_session_dao import StudySessionDAO
from app.services.ai_service import AIService
from app.services.flashcard_service import FlashcardService
from app.services.stats_service import StatsService
from app.schemas.flashcard_schema import FlashcardCreate
from app.schemas.stats_schema import StudySessionCreate
from app.middlewares.auth_middleware import jwt_required_middleware
from app.middlewares.error_handler import ResourceNotFoundError, ForbiddenError

blurting_bp = Blueprint("blurting", __name__)

note_dao = NoteDAO(db.session)
deck_dao = DeckDAO(db.session)
flashcard_dao = FlashcardDAO(db.session)
study_session_dao = StudySessionDAO(db.session)

ai_service = AIService()
flashcard_service = FlashcardService(flashcard_dao, deck_dao)
stats_service = StatsService(study_session_dao, deck_dao, flashcard_dao)

@blurting_bp.route("/analyze", methods=["POST"])
@jwt_required_middleware
def analyze():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    
    note_id = data.get("note_id")
    user_blurting = data.get("user_blurting")
    duration_seconds = data.get("duration_seconds", 0)
    
    if not note_id or not user_blurting:
        return jsonify({
            "error": {
                "code": "BAD_REQUEST",
                "message": "note_id et user_blurting sont requis pour lancer l'analyse.",
                "details": {}
            }
        }), 400
        
    note = note_dao.get_by_id(note_id)
    if not note:
        raise ResourceNotFoundError("Note introuvable.")
    if note.user_id != user_id:
        raise ForbiddenError("Accès interdit à cette note.")
        
    # Lancement de l'analyse IA
    analysis_result = ai_service.analyze_blurting(note.title, note.content, user_blurting)
    
    # Enregistrement de la session d'étude si la durée est valide
    if duration_seconds > 0:
        session_data = StudySessionCreate(
            module="note",
            duration_seconds=duration_seconds,
            cards_reviewed=0,
            cards_correct=0
        )
        stats_service.create_session(user_id, session_data)
        
    return jsonify(analysis_result), 200

@blurting_bp.route("/create-flashcards", methods=["POST"])
@jwt_required_middleware
def create_flashcards():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    
    deck_id = data.get("deck_id")
    flashcards = data.get("flashcards", [])
    
    if not deck_id or not flashcards:
        return jsonify({
            "error": {
                "code": "BAD_REQUEST",
                "message": "deck_id et flashcards sont requis.",
                "details": {}
            }
        }), 400
        
    deck = deck_dao.get_by_id(deck_id)
    if not deck:
        raise ResourceNotFoundError("Deck introuvable.")
    if deck.user_id != user_id:
        raise ForbiddenError("Accès interdit à ce deck.")
        
    created_cards = []
    for card_data in flashcards:
        front = card_data.get("front")
        back = card_data.get("back")
        if not front or not back:
            continue
            
        card_create = FlashcardCreate(front=front, back=back)
        created_card = flashcard_service.create_flashcard(user_id, deck_id, card_create)
        created_cards.append(created_card)
        
    return jsonify({
        "created_count": len(created_cards),
        "flashcards": [c.model_dump() for c in created_cards]
    }), 201
