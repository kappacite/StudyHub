from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from datetime import datetime
from app.extensions import db, limiter
from app.dao.note_dao import NoteDAO
from app.dao.deck_dao import DeckDAO
from app.dao.flashcard_dao import FlashcardDAO
from app.dao.study_session_dao import StudySessionDAO
from app.services.flashcard_service import FlashcardService
from app.schemas.flashcard_schema import FlashcardCreate
from app.middlewares.auth_middleware import jwt_required_middleware
from app.middlewares.error_handler import ResourceNotFoundError, ForbiddenError
from app.tasks import run_blurting_analysis
from app.utils.task_dispatch import dispatch_or_run
from celery.result import AsyncResult

blurting_bp = Blueprint("blurting", __name__)

note_dao = NoteDAO(db.session)
deck_dao = DeckDAO(db.session)
flashcard_dao = FlashcardDAO(db.session)
study_session_dao = StudySessionDAO(db.session)

flashcard_service = FlashcardService(flashcard_dao, deck_dao)

def get_user_identity_or_ip():
    try:
        identity = get_jwt_identity()
        if identity:
            return str(identity)
    except Exception:
        pass
    from flask_limiter.util import get_remote_address
    return get_remote_address()

@blurting_bp.route("/analyze", methods=["POST"])
@jwt_required_middleware
@limiter.limit("10 per hour", key_func=get_user_identity_or_ip)
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
        
    # Lancement de l'analyse IA via Celery, avec repli synchrone si le broker
    # Redis est indisponible (dev sans worker).
    mode, payload = dispatch_or_run(
        run_blurting_analysis, user_id, note_id, user_blurting, duration_seconds
    )
    if mode == "async":
        return jsonify({"task_id": payload.id, "status": payload.status}), 202
    # Repli synchrone : résultat déjà prêt, le frontend court-circuite le polling.
    return jsonify({"status": "SUCCESS", "result": payload}), 200

@blurting_bp.route("/tasks/<task_id>", methods=["GET"])
@jwt_required_middleware
def get_task_status(task_id):
    result = AsyncResult(task_id)
    
    response = {
        "task_id": task_id,
        "status": result.status
    }
    
    if result.ready():
        if result.successful():
            response["result"] = result.result
        else:
            response["error"] = {
                "code": "TASK_FAILED",
                "message": str(result.result) or "Une erreur est survenue lors de l'analyse.",
                "details": {}
            }
            
    return jsonify(response), 200


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
