import logging
from flask import jsonify
from werkzeug.exceptions import HTTPException
from pydantic import ValidationError as PydanticValidationError

logger = logging.getLogger(__name__)

class AppError(Exception):
    def __init__(self, message: str, code: str = "BAD_REQUEST", status_code: int = 400, details: dict = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}

class ValidationError(AppError):
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, code="VALIDATION_ERROR", status_code=400, details=details)

class UnauthorizedError(AppError):
    def __init__(self, message: str = "Non authentifié."):
        super().__init__(message, code="UNAUTHORIZED", status_code=401)

class ForbiddenError(AppError):
    def __init__(self, message: str = "Accès interdit."):
        super().__init__(message, code="FORBIDDEN", status_code=403)

class ResourceNotFoundError(AppError):
    def __init__(self, message: str = "Ressource introuvable."):
        super().__init__(message, code="RESOURCE_NOT_FOUND", status_code=404)

class ConflictError(AppError):
    def __init__(self, message: str):
        super().__init__(message, code="CONFLICT", status_code=409)

def register_error_handlers(app):
    
    @app.errorhandler(AppError)
    def handle_app_error(err):
        response = {
            "error": {
                "code": err.code,
                "message": err.message,
                "details": err.details
            }
        }
        return jsonify(response), err.status_code

    @app.errorhandler(PydanticValidationError)
    def handle_pydantic_validation_error(err):
        # Traduction des erreurs Pydantic pour le client
        details = {}
        for error in err.errors():
            loc = ".".join(str(x) for x in error["loc"])
            details[loc] = error["msg"]
            
        response = {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Erreur de validation des données.",
                "details": details
            }
        }
        return jsonify(response), 400

    @app.errorhandler(HTTPException)
    def handle_http_exception(err):
        response = {
            "error": {
                "code": err.name.upper().replace(" ", "_"),
                "message": err.description,
                "details": {}
            }
        }
        return jsonify(response), err.code

    @app.errorhandler(Exception)
    def handle_generic_exception(err):
        logger.exception("Une erreur inattendue est survenue : %s", str(err))
        
        # En mode debug, on peut renvoyer plus de détails si besoin
        # Mais AGENTS.md stipule: "500 -> erreur générique sans stack trace en production"
        is_debug = app.config.get("DEBUG", False)
        
        response = {
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": str(err) if is_debug else "Une erreur interne du serveur est survenue.",
                "details": {}
            }
        }
        return jsonify(response), 500
