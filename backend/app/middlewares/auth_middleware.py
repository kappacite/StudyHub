from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.extensions import jwt

def jwt_required_middleware(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        verify_jwt_in_request()
        return f(*args, **kwargs)
    return decorated

# Enregistrement des callbacks de formatage d'erreur pour Flask-JWT-Extended
@jwt.unauthorized_loader
def unauthorized_callback(err_str):
    return jsonify({
        "error": {
            "code": "UNAUTHORIZED",
            "message": err_str or "Token d'authentification manquant.",
            "details": {}
        }
    }), 401

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        "error": {
            "code": "UNAUTHORIZED",
            "message": "La session a expiré. Veuillez vous reconnecter.",
            "details": {}
        }
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(err_str):
    return jsonify({
        "error": {
            "code": "UNAUTHORIZED",
            "message": "Le jeton d'authentification est invalide.",
            "details": {}
        }
    }), 401

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({
        "error": {
            "code": "UNAUTHORIZED",
            "message": "Ce jeton a été révoqué.",
            "details": {}
        }
    }), 401
