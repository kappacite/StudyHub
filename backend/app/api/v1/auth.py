from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.dao.user_dao import UserDAO
from app.services.auth_service import AuthService
from app.schemas.user_schema import UserCreate
from app.schemas.auth_schema import LoginRequest
from app.middlewares.auth_middleware import jwt_required_middleware

auth_bp = Blueprint("auth", __name__)

# Instanciation manuelle (injection de dépendance)
user_dao = UserDAO(db.session)
auth_service = AuthService(user_dao)

@auth_bp.route("/register", methods=["POST"])
def register():
    data_dict = request.get_json() or {}
    
    # Validation des entrées avec Pydantic v2
    user_create = UserCreate.model_validate(data_dict)
    
    # Appel service
    result = auth_service.register(user_create)
    
    # Retourner l'utilisateur créé
    return jsonify(result.model_dump()), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data_dict = request.get_json() or {}
    
    # Validation des entrées
    login_req = LoginRequest.model_validate(data_dict)
    
    # Appel service
    result = auth_service.login(login_req)
    
    return jsonify(result.model_dump()), 200

@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    # Récupérer l'identité de l'utilisateur à partir du refresh token
    user_identity = get_jwt_identity()
    
    result = auth_service.refresh_access_token(user_identity)
    return jsonify(result.model_dump()), 200

@auth_bp.route("/logout", methods=["POST"])
def logout():
    # Version simple : pas d'état sur le serveur.
    # Pour révoquer, il faudrait enregistrer le token dans un cache Redis ou DB.
    # Renvoyer 204 suffit à indiquer le succès côté client.
    return "", 204

@auth_bp.route("/account", methods=["DELETE"])
@jwt_required_middleware
def delete_account():
    # Obtenir l'identité de l'utilisateur connecté (ID de l'utilisateur)
    user_id = int(get_jwt_identity())
    
    auth_service.delete_account(user_id)
    return "", 204
