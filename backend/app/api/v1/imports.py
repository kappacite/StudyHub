from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.extensions import db
from app.dao.deck_dao import DeckDAO
from app.dao.flashcard_dao import FlashcardDAO
from app.dao.tag_dao import TagDAO
from app.services.import_service import ImportService
from app.middlewares.auth_middleware import jwt_required_middleware

imports_bp = Blueprint("imports", __name__)

deck_dao = DeckDAO(db.session)
flashcard_dao = FlashcardDAO(db.session)
tag_dao = TagDAO(db.session)
import_service = ImportService(deck_dao, flashcard_dao, tag_dao)

@imports_bp.route("/anki", methods=["POST"])
@jwt_required_middleware
def import_anki():
    user_id = int(get_jwt_identity())
    
    # Vérifie si le fichier est présent
    if "file" not in request.files:
        return jsonify({
            "error": {
                "code": "BAD_REQUEST",
                "message": "Aucun fichier fourni dans la requête (clé 'file' manquante)."
            }
        }), 400
        
    file = request.files["file"]
    if file.filename == "":
        return jsonify({
            "error": {
                "code": "BAD_REQUEST",
                "message": "Aucun fichier n'a été sélectionné."
            }
        }), 400
        
    # Validation de l'extension
    if not file.filename.lower().endswith(".apkg"):
        return jsonify({
            "error": {
                "code": "BAD_REQUEST",
                "message": "Format invalide. Seuls les fichiers .apkg d'Anki sont supportés."
            }
        }), 400

    # Lecture des données en mémoire
    file_bytes = file.read()
    
    # Validation de la taille (50 Mo maximum)
    max_size = 50 * 1024 * 1024
    if len(file_bytes) > max_size:
        return jsonify({
            "error": {
                "code": "PAYLOAD_TOO_LARGE",
                "message": "Le fichier dépasse la limite de taille autorisée de 50 Mo."
            }
        }), 413

    # Récupération de binder_id (optionnel)
    binder_id = request.form.get("binder_id")
    if binder_id:
        try:
            binder_id = int(binder_id)
        except ValueError:
            return jsonify({
                "error": {
                    "code": "BAD_REQUEST",
                    "message": "Le paramètre binder_id doit être un nombre entier."
                }
            }), 400
    else:
        binder_id = None
        
    try:
        result = import_service.import_anki(user_id, file_bytes, binder_id)
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({
            "error": {
                "code": "BAD_REQUEST",
                "message": str(e)
            }
        }), 400
    except Exception as e:
        return jsonify({
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Une erreur interne est survenue lors du traitement du fichier.",
                "details": str(e)
            }
        }), 500
