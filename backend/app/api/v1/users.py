from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.extensions import db
from app.dao.user_dao import UserDAO
from app.services.user_service import UserService
from app.schemas.user_schema import UserUpdate
from app.middlewares.auth_middleware import jwt_required_middleware

users_bp = Blueprint("users", __name__)

user_dao = UserDAO(db.session)
user_service = UserService(user_dao)

@users_bp.route("/me", methods=["GET"])
@jwt_required_middleware
def get_me():
    user_id = int(get_jwt_identity())
    result = user_service.get_profile(user_id)
    return jsonify(result.model_dump()), 200

@users_bp.route("/me", methods=["PUT"])
@jwt_required_middleware
def update_me():
    user_id = int(get_jwt_identity())
    data_dict = request.get_json() or {}
    
    # Validation
    user_update = UserUpdate.model_validate(data_dict)
    
    result = user_service.update_profile(user_id, user_update)
    return jsonify(result.model_dump()), 200

@users_bp.route("/me", methods=["DELETE"])
@jwt_required_middleware
def delete_me():
    user_id = int(get_jwt_identity())
    user_service.delete_account(user_id)
    return "", 204
