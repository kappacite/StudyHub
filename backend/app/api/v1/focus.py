from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.services.focus_service import FocusService
from app.middlewares.auth_middleware import jwt_required_middleware

focus_bp = Blueprint("focus", __name__)
focus_service = FocusService()

@focus_bp.route("/today", methods=["GET"])
@jwt_required_middleware
def get_focus_today():
    user_id = int(get_jwt_identity())
    result = focus_service.get_today_items(user_id)
    return jsonify(result.model_dump()), 200

@focus_bp.route("/forecast", methods=["GET"])
@jwt_required_middleware
def get_focus_forecast():
    user_id = int(get_jwt_identity())
    days = request.args.get("days", 14, type=int)
    result = focus_service.get_forecast(user_id, days)
    return jsonify(result.model_dump()), 200

@focus_bp.route("/retention", methods=["GET"])
@jwt_required_middleware
def get_focus_retention():
    user_id = int(get_jwt_identity())
    result = focus_service.get_retention_by_subject(user_id)
    return jsonify(result.model_dump()), 200
