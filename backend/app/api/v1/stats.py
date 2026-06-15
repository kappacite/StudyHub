from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.extensions import db
from app.dao.study_session_dao import StudySessionDAO
from app.dao.deck_dao import DeckDAO
from app.dao.flashcard_dao import FlashcardDAO
from app.dao.revision_dao import RevisionSetDAO, RevisionItemDAO
from app.services.stats_service import StatsService
from app.services.revision_stats_service import RevisionStatsService
from app.schemas.stats_schema import StudySessionCreate
from app.middlewares.auth_middleware import jwt_required_middleware
from app.utils.cache import cache_route

stats_bp = Blueprint("stats", __name__)

study_session_dao = StudySessionDAO(db.session)
deck_dao = DeckDAO(db.session)
flashcard_dao = FlashcardDAO(db.session)
revision_set_dao = RevisionSetDAO(db.session)
revision_item_dao = RevisionItemDAO(db.session)

stats_service = StatsService(study_session_dao, deck_dao, flashcard_dao)
revision_stats_service = RevisionStatsService(revision_set_dao, revision_item_dao, study_session_dao)

@stats_bp.route("/overview", methods=["GET"])
@jwt_required_middleware
@cache_route(timeout=300)
def get_overview():
    user_id = int(get_jwt_identity())
    result = stats_service.get_overview(user_id)
    return jsonify(result.model_dump()), 200

@stats_bp.route("/sessions", methods=["GET"])
@jwt_required_middleware
def get_sessions():
    user_id = int(get_jwt_identity())
    
    start_date = request.args.get("from")
    end_date = request.args.get("to")
    module = request.args.get("module")
    
    result = stats_service.get_sessions(user_id, start_date, end_date, module)
    return jsonify([s.model_dump() for s in result]), 200

@stats_bp.route("/sessions", methods=["POST"])
@jwt_required_middleware
def create_session():
    user_id = int(get_jwt_identity())
    data_dict = request.get_json() or {}
    
    session_create = StudySessionCreate.model_validate(data_dict)
    
    result = stats_service.create_session(user_id, session_create)
    return jsonify(result.model_dump()), 201

@stats_bp.route("/heatmap", methods=["GET"])
@jwt_required_middleware
@cache_route(timeout=300)
def get_heatmap():
    user_id = int(get_jwt_identity())
    result = stats_service.get_heatmap(user_id)
    return jsonify([item.model_dump() for item in result]), 200

@stats_bp.route("/decks/<int:deck_id>", methods=["GET"])
@jwt_required_middleware
@cache_route(timeout=300)
def get_deck_stats(deck_id):
    user_id = int(get_jwt_identity())
    result = stats_service.get_deck_stats(user_id, deck_id)
    return jsonify(result.model_dump()), 200

@stats_bp.route("/dashboard", methods=["GET"])
@jwt_required_middleware
@cache_route(timeout=300)
def get_dashboard():
    user_id = int(get_jwt_identity())
    result = stats_service.get_dashboard_stats(user_id)
    return jsonify(result.model_dump()), 200

# --- Statistiques par élément de révision (A7 / D5) --------------------------

@stats_bp.route("/sets/<int:set_id>", methods=["GET"])
@jwt_required_middleware
def get_set_stats(set_id):
    user_id = int(get_jwt_identity())
    result = revision_stats_service.get_set_stats(user_id, set_id)
    return jsonify(result.model_dump(mode="json")), 200

@stats_bp.route("/items/<int:item_id>", methods=["GET"])
@jwt_required_middleware
def get_item_stats(item_id):
    user_id = int(get_jwt_identity())
    result = revision_stats_service.get_item_stats(user_id, item_id)
    return jsonify(result.model_dump(mode="json")), 200

@stats_bp.route("/binders/<binder_id>", methods=["GET"])
@jwt_required_middleware
def get_binder_stats(binder_id):
    user_id = int(get_jwt_identity())
    include_descendants = request.args.get("descendants", "true").lower() != "false"
    result = revision_stats_service.get_binder_stats(user_id, binder_id, include_descendants)
    return jsonify(result.model_dump(mode="json")), 200
