from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from datetime import datetime
from app.extensions import db
from app.dao.flashcard_dao import FlashcardDAO
from app.dao.deck_dao import DeckDAO
from app.services.planning_service import PlanningService
from app.schemas.planning_schema import PlanningCalendarResponse, PlanningAdvanceRequest
from app.schemas.flashcard_schema import FlashcardResponse
from app.middlewares.auth_middleware import jwt_required_middleware

planning_bp = Blueprint("planning", __name__)

flashcard_dao = FlashcardDAO(db.session)
deck_dao = DeckDAO(db.session)
planning_service = PlanningService(flashcard_dao, deck_dao)

@planning_bp.route("/calendar", methods=["GET"])
@jwt_required_middleware
def get_planning_calendar():
    user_id = int(get_jwt_identity())
    
    from_str = request.args.get("from")
    to_str = request.args.get("to")
    
    if not from_str or not to_str:
        return jsonify({
            "error": {
                "code": "BAD_REQUEST",
                "message": "Les paramètres 'from' et 'to' sont requis."
            }
        }), 400
        
    try:
        date_from = datetime.strptime(from_str, "%Y-%m-%d").date()
        date_to = datetime.strptime(to_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({
            "error": {
                "code": "BAD_REQUEST",
                "message": "Le format des dates doit être YYYY-MM-DD."
            }
        }), 400
        
    result = planning_service.get_calendar(user_id, date_from, date_to)
    response_data = PlanningCalendarResponse(**result).model_dump()
    return jsonify(response_data), 200

@planning_bp.route("/advance", methods=["POST"])
@jwt_required_middleware
def post_planning_advance():
    user_id = int(get_jwt_identity())
    body = request.get_json()
    
    if not body:
        return jsonify({
            "error": {
                "code": "BAD_REQUEST",
                "message": "Le corps de la requête est vide."
            }
        }), 400
        
    try:
        req_data = PlanningAdvanceRequest(**body)
    except Exception as e:
        return jsonify({
            "error": {
                "code": "BAD_REQUEST",
                "message": f"Validation échouée : {str(e)}"
            }
        }), 400
        
    cards = planning_service.advance_review(user_id, req_data.deck_id, req_data.card_ids, req_data.date)
    response_data = [FlashcardResponse.model_validate(c).model_dump() for c in cards]
    return jsonify(response_data), 200
