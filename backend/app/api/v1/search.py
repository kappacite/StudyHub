from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.extensions import db
from app.dao.search_dao import SearchDAO
from app.services.search_service import SearchService
from app.middlewares.auth_middleware import jwt_required_middleware

search_bp = Blueprint("search", __name__)

search_dao = SearchDAO(db.session)
search_service = SearchService(search_dao)

@search_bp.route("", methods=["GET"])
@jwt_required_middleware
def get_search():
    user_id = int(get_jwt_identity())
    query = request.args.get("q", "").strip()
    
    if not query or len(query) < 2:
        return jsonify({
            "error": {
                "code": "BAD_REQUEST",
                "message": "La requête de recherche doit contenir au moins 2 caractères."
            }
        }), 400
        
    types_str = request.args.get("types", "note,deck,flashcard,diagram")
    types = [t.strip() for t in types_str.split(",") if t.strip()]
    limit = request.args.get("limit", 20, type=int)
    
    result = search_service.search(user_id, query, types, limit)
    return jsonify(result), 200
