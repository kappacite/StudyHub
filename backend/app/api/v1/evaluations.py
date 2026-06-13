from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.extensions import db, limiter
from app.dao.evaluation_dao import EvaluationDAO
from app.dao.note_dao import NoteDAO
from app.dao.deck_dao import DeckDAO
from app.dao.flashcard_dao import FlashcardDAO
from app.services.evaluation_service import EvaluationService
from app.services.ai_service import AIService
from app.schemas.evaluation_schema import (
    EvaluationGenerateRequest,
    EvaluationAnswerRequest,
)
from app.middlewares.auth_middleware import jwt_required_middleware
from app.middlewares.error_handler import ResourceNotFoundError, ForbiddenError
from app.tasks import run_evaluation_generation
from celery.result import AsyncResult

evaluations_bp = Blueprint("evaluations", __name__)

# Initialisation des DAOs / Services
evaluation_dao = EvaluationDAO(db.session)
note_dao = NoteDAO(db.session)
deck_dao = DeckDAO(db.session)
flashcard_dao = FlashcardDAO(db.session)
ai_service = AIService()
evaluation_service = EvaluationService(
    evaluation_dao, note_dao, ai_service, deck_dao=deck_dao, flashcard_dao=flashcard_dao
)


def get_user_identity_or_ip():
    try:
        identity = get_jwt_identity()
        if identity:
            return str(identity)
    except Exception:
        pass
    from flask_limiter.util import get_remote_address
    return get_remote_address()


@evaluations_bp.route("/generate", methods=["POST"])
@jwt_required_middleware
@limiter.limit("10 per hour", key_func=get_user_identity_or_ip)
def generate():
    user_id = int(get_jwt_identity())
    req = EvaluationGenerateRequest.model_validate(request.get_json() or {})

    # Pré-vérification d'appartenance : 404/403 synchrone avant de lancer la tâche.
    note = note_dao.get_by_id(req.note_id)
    if not note:
        raise ResourceNotFoundError("Note introuvable.")
    if note.user_id != user_id:
        raise ForbiddenError("Accès interdit à cette note.")

    task = run_evaluation_generation.delay(user_id, req.note_id, req.item_count, req.force)
    return jsonify({"task_id": task.id, "status": task.status}), 202


@evaluations_bp.route("/tasks/<task_id>", methods=["GET"])
@jwt_required_middleware
def get_task_status(task_id):
    result = AsyncResult(task_id)
    response = {"task_id": task_id, "status": result.status}

    if result.ready():
        if result.successful():
            response["result"] = result.result
        else:
            response["error"] = {
                "code": "TASK_FAILED",
                "message": str(result.result) or "Une erreur est survenue lors de la génération.",
                "details": {},
            }

    return jsonify(response), 200


@evaluations_bp.route("/<int:evaluation_id>", methods=["GET"])
@jwt_required_middleware
def get_evaluation(evaluation_id):
    user_id = int(get_jwt_identity())
    resp = evaluation_service.get_evaluation(user_id, evaluation_id)
    return jsonify(resp.model_dump(mode="json")), 200


@evaluations_bp.route("/<int:evaluation_id>/items/<int:item_id>/answer", methods=["POST"])
@jwt_required_middleware
def answer_item(evaluation_id, item_id):
    user_id = int(get_jwt_identity())
    req = EvaluationAnswerRequest.model_validate(request.get_json() or {})
    resp = evaluation_service.answer_item(
        user_id, evaluation_id, item_id, req.value, req.self_grade
    )
    return jsonify(resp.model_dump(mode="json")), 200


@evaluations_bp.route("/<int:evaluation_id>/complete", methods=["POST"])
@jwt_required_middleware
def complete(evaluation_id):
    user_id = int(get_jwt_identity())
    resp = evaluation_service.complete_evaluation(user_id, evaluation_id)
    return jsonify(resp.model_dump(mode="json")), 200
