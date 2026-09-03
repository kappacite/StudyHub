from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.extensions import db, limiter, celery_app
from app.dao.note_dao import NoteDAO
from app.dao.note_grade_dao import NoteGradeDAO
from app.middlewares.auth_middleware import jwt_required_middleware
from app.middlewares.error_handler import ResourceNotFoundError
from app.schemas.note_grade_schema import NoteGradeResponse
from app.tasks import run_note_grading
from app.utils.task_dispatch import dispatch_or_run
from app.utils.security import check_note_access

notation_bp = Blueprint("notation", __name__)

note_dao = NoteDAO(db.session)
note_grade_dao = NoteGradeDAO(db.session)


def get_user_identity_or_ip():
    try:
        identity = get_jwt_identity()
        if identity:
            return str(identity)
    except Exception:
        pass
    from flask_limiter.util import get_remote_address
    return get_remote_address()


@notation_bp.route("/grade", methods=["POST"])
@jwt_required_middleware
@limiter.limit("10 per hour", key_func=get_user_identity_or_ip)
def grade():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    note_id = data.get("note_id")
    if not note_id:
        return jsonify({
            "error": {
                "code": "BAD_REQUEST",
                "message": "note_id est requis pour lancer la notation.",
                "details": {}
            }
        }), 400

    note = note_dao.get_by_id(note_id)
    if not note:
        raise ResourceNotFoundError("Note introuvable.")
    # Notation autorisée sur une note partagée en lecture, même principe que
    # feynman/blurting (révision active).
    check_note_access(db.session, note, user_id)

    mode, payload = dispatch_or_run(run_note_grading, user_id, note_id)
    if mode == "async":
        return jsonify({"task_id": payload.id, "status": payload.status}), 202
    return jsonify({"status": "SUCCESS", "result": payload}), 200


@notation_bp.route("/<note_id>", methods=["GET"])
@jwt_required_middleware
def get_existing_grade(note_id):
    """notes-ia-planning-corrections, Task 12 : notation deja enregistree pour cette
    note, si elle existe (404 sinon) -- permet au frontend de proposer voir/reevaluer
    plutot que de relancer l'IA a chaque clic."""
    user_id = int(get_jwt_identity())

    note = note_dao.get_by_id(note_id)
    if not note:
        raise ResourceNotFoundError("Note introuvable.")
    check_note_access(db.session, note, user_id)

    grade = note_grade_dao.get_by_note(note._id)
    if not grade:
        raise ResourceNotFoundError("Pas encore de notation pour cette note.")

    return jsonify(NoteGradeResponse.model_validate(grade).model_dump(mode="json")), 200


@notation_bp.route("/tasks/<task_id>", methods=["GET"])
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
                "message": str(result.result) or "Une erreur est survenue lors de la notation.",
                "details": {}
            }
    return jsonify(response), 200
