from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.extensions import db, limiter, celery_app
from app.dao.note_dao import NoteDAO
from app.middlewares.auth_middleware import jwt_required_middleware
from app.middlewares.error_handler import ResourceNotFoundError
from app.tasks import run_feynman_analysis
from app.utils.task_dispatch import dispatch_or_run

feynman_bp = Blueprint("feynman", __name__)

note_dao = NoteDAO(db.session)


def get_user_identity_or_ip():
    try:
        identity = get_jwt_identity()
        if identity:
            return str(identity)
    except Exception:
        pass
    from flask_limiter.util import get_remote_address
    return get_remote_address()


@feynman_bp.route("/analyze", methods=["POST"])
@jwt_required_middleware
@limiter.limit("10 per hour", key_func=get_user_identity_or_ip)
def analyze():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    note_id = data.get("note_id")
    user_explanation = data.get("user_explanation")
    duration_seconds = data.get("duration_seconds", 0)

    if not note_id or not user_explanation:
        return jsonify({
            "error": {
                "code": "BAD_REQUEST",
                "message": "note_id et user_explanation sont requis pour lancer l'analyse.",
                "details": {}
            }
        }), 400

    note = note_dao.get_by_id(note_id)
    if not note:
        raise ResourceNotFoundError("Note introuvable.")
    # Autorise aussi l'exercice Feynman sur une note partagée (lecture seule).
    from app.utils.security import check_note_access
    check_note_access(db.session, note, user_id)

    mode, payload = dispatch_or_run(
        run_feynman_analysis, user_id, note_id, user_explanation, duration_seconds
    )
    if mode == "async":
        return jsonify({"task_id": payload.id, "status": payload.status}), 202
    return jsonify({"status": "SUCCESS", "result": payload}), 200


@feynman_bp.route("/tasks/<task_id>", methods=["GET"])
@jwt_required_middleware
def get_task_status(task_id):
    result = celery_app.AsyncResult(task_id)
    response = {"task_id": task_id, "status": result.status}
    if result.ready():
        if result.successful():
            response["result"] = result.result
        else:
            response["error"] = {
                "code": "TASK_FAILED",
                "message": str(result.result) or "Une erreur est survenue lors de l'analyse.",
                "details": {}
            }
    return jsonify(response), 200
