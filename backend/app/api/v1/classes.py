"""
Blueprint pour les espaces de cours (classes).

Endpoints :
  POST   /api/v1/classes                                  → créer une classe
  GET    /api/v1/classes/:id/assignments                  → liste des devoirs
  POST   /api/v1/classes/:id/assignments                  → créer un devoir (teacher)
  GET    /api/v1/classes/:id/assignments/:asgn_id         → détails + progression (teacher)
  DELETE /api/v1/classes/:id/assignments/:asgn_id         → supprimer un devoir (teacher)
  GET    /api/v1/classes/:id/students/:user_id/progress   → progression individuelle (teacher)
  GET    /api/v1/assignments/mine                         → devoirs assignés à moi (élève)
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.dao.group_dao import GroupDAO
from app.dao.binder_dao import BinderDAO
from app.dao.user_dao import UserDAO
from app.extensions import db, celery_app
from app.schemas.class_schema import (
    ClassCreateSchema, AssignmentCreateSchema, TaskSubmitSchema, AssignmentGradeSchema,
)
from app.schemas.analytics_schema import ClassInsightSchema
from app.schemas.engagement_schema import AnnouncementCreateSchema
from app.services.class_service import ClassService
from app.services.analytics_service import AnalyticsService
from app.services.engagement_service import EngagementService
from app.tasks import run_class_gap_analysis
from app.utils.task_dispatch import dispatch_or_run
from app.middlewares.error_handler import ValidationError

classes_bp = Blueprint("classes", __name__)
assignments_mine_bp = Blueprint("assignments_mine", __name__)


def _make_service() -> ClassService:
    return ClassService(
        group_dao=GroupDAO(db.session),
        binder_dao=BinderDAO(db.session),
        user_dao=UserDAO(db.session)
    )


def _make_analytics() -> AnalyticsService:
    return AnalyticsService(group_dao=GroupDAO(db.session))


def _make_engagement() -> EngagementService:
    return EngagementService(group_dao=GroupDAO(db.session))


# ─── Lister/Créer une classe ───────────────────────────────────────────────────

@classes_bp.route("", methods=["GET"])
@jwt_required()
def get_my_classes():
    user_id = int(get_jwt_identity())
    service = _make_service()
    result = service.get_my_classes(user_id)
    return jsonify([c.model_dump(mode="json") for c in result]), 200


@classes_bp.route("", methods=["POST"])
@jwt_required()
def create_class():
    user_id = int(get_jwt_identity())
    body = request.get_json() or {}
    try:
        data = ClassCreateSchema(**body)
    except Exception as e:
        raise ValidationError(str(e))

    service = _make_service()
    result = service.create_class(user_id, data)
    return jsonify(result.model_dump(mode="json")), 201


# ─── Devoirs d'une classe ─────────────────────────────────────────────────────

@classes_bp.route("/<int:class_id>/assignments", methods=["GET"])
@jwt_required()
def list_assignments(class_id: int):
    user_id = int(get_jwt_identity())
    service = _make_service()
    asgns = service.list_assignments(class_id, user_id)
    return jsonify([a.model_dump(mode="json") for a in asgns]), 200


@classes_bp.route("/<int:class_id>/assignments", methods=["POST"])
@jwt_required()
def create_assignment(class_id: int):
    user_id = int(get_jwt_identity())
    body = request.get_json() or {}
    try:
        data = AssignmentCreateSchema(**body)
    except Exception as e:
        raise ValidationError(str(e))

    service = _make_service()
    result = service.create_assignment(class_id, user_id, data)
    return jsonify(result.model_dump(mode="json")), 201


@classes_bp.route("/<int:class_id>/assignments/<int:asgn_id>", methods=["GET"])
@jwt_required()
def get_assignment(class_id: int, asgn_id: int):
    user_id = int(get_jwt_identity())
    service = _make_service()
    result = service.get_assignment(class_id, asgn_id, user_id)
    return jsonify(result.model_dump(mode="json")), 200


@classes_bp.route("/<int:class_id>/assignments/<int:asgn_id>", methods=["DELETE"])
@jwt_required()
def delete_assignment(class_id: int, asgn_id: int):
    user_id = int(get_jwt_identity())
    service = _make_service()
    service.delete_assignment(class_id, asgn_id, user_id)
    return "", 204


@classes_bp.route(
    "/<int:class_id>/assignments/<int:asgn_id>/tasks/<int:task_id>/submit",
    methods=["POST"],
)
@jwt_required()
def submit_task(class_id: int, asgn_id: int, task_id: int):
    user_id = int(get_jwt_identity())
    body = request.get_json(silent=True) or {}
    try:
        data = TaskSubmitSchema(**body)
    except Exception as e:
        raise ValidationError(str(e))

    service = _make_service()
    result = service.submit_task(class_id, asgn_id, task_id, user_id, data)
    return jsonify(result.model_dump(mode="json")), 200


@classes_bp.route(
    "/<int:class_id>/assignments/<int:asgn_id>/submissions/<int:student_id>",
    methods=["PATCH"],
)
@jwt_required()
def grade_submission(class_id: int, asgn_id: int, student_id: int):
    teacher_id = int(get_jwt_identity())
    body = request.get_json() or {}
    try:
        data = AssignmentGradeSchema(**body)
    except Exception as e:
        raise ValidationError(str(e))

    service = _make_service()
    result = service.grade_submission(class_id, asgn_id, student_id, teacher_id, data)
    return jsonify(result.model_dump(mode="json")), 200


# ─── Tableau de bord analytique (professeur) ──────────────────────────────────

@classes_bp.route("/<int:class_id>/analytics", methods=["GET"])
@jwt_required()
def get_class_analytics(class_id: int):
    user_id = int(get_jwt_identity())
    analytics = _make_analytics()
    result = analytics.get_class_overview(class_id, user_id)
    return jsonify(result.model_dump(mode="json")), 200


@classes_bp.route("/<int:class_id>/insights", methods=["GET"])
@jwt_required()
def get_class_insights(class_id: int):
    user_id = int(get_jwt_identity())
    # Vérifie le rôle professeur, puis renvoie le dernier cache (ou vide).
    _make_analytics()._require_teacher(class_id, user_id)
    from app.models.class_insight import ClassInsight
    latest = (
        db.session.query(ClassInsight)
        .filter(ClassInsight.group_id == class_id)
        .order_by(ClassInsight.created_at.desc(), ClassInsight.id.desc())
        .first()
    )
    if not latest:
        return jsonify(ClassInsightSchema(class_id=class_id).model_dump(mode="json")), 200
    payload = latest.payload or {}
    return jsonify(ClassInsightSchema(
        class_id=class_id,
        weak_topics=payload.get("weak_topics", []),
        summary=payload.get("summary", ""),
        ai=payload.get("ai", False),
        created_at=latest.created_at,
    ).model_dump(mode="json")), 200


@classes_bp.route("/<int:class_id>/insights", methods=["POST"])
@jwt_required()
def refresh_class_insights(class_id: int):
    user_id = int(get_jwt_identity())
    _make_analytics()._require_teacher(class_id, user_id)
    mode, payload = dispatch_or_run(run_class_gap_analysis, class_id)
    if mode == "async":
        return jsonify({"task_id": payload.id, "status": payload.status}), 202
    return jsonify({"status": "SUCCESS", "result": payload}), 200


# ─── Engagement : annonces, fil & classement ──────────────────────────────────

@classes_bp.route("/<int:class_id>/announcements", methods=["POST"])
@jwt_required()
def post_announcement(class_id: int):
    user_id = int(get_jwt_identity())
    body = request.get_json() or {}
    try:
        data = AnnouncementCreateSchema(**body)
    except Exception as e:
        raise ValidationError(str(e))
    result = _make_engagement().post_announcement(class_id, user_id, data)
    return jsonify(result.model_dump(mode="json")), 201


@classes_bp.route("/<int:class_id>/feed", methods=["GET"])
@jwt_required()
def get_feed(class_id: int):
    user_id = int(get_jwt_identity())
    result = _make_engagement().get_feed(class_id, user_id)
    return jsonify([f.model_dump(mode="json") for f in result]), 200


@classes_bp.route("/<int:class_id>/leaderboard", methods=["GET"])
@jwt_required()
def get_leaderboard(class_id: int):
    user_id = int(get_jwt_identity())
    result = _make_engagement().get_leaderboard(class_id, user_id)
    return jsonify(result.model_dump(mode="json")), 200


# ─── Progression élève ────────────────────────────────────────────────────────

@classes_bp.route("/<int:class_id>/students/<int:student_id>/progress", methods=["GET"])
@jwt_required()
def get_student_progress(class_id: int, student_id: int):
    requester_id = int(get_jwt_identity())
    service = _make_service()
    result = service.get_student_progress(class_id, student_id, requester_id)
    return jsonify([r.model_dump(mode="json") for r in result]), 200


@classes_bp.route("/<int:class_id>/materials/progress", methods=["GET"])
@jwt_required()
def get_class_materials_progress(class_id: int):
    user_id = int(get_jwt_identity())
    service = _make_service()
    result = service.get_class_materials_progress(class_id, user_id)
    return jsonify([r.model_dump(mode="json") for r in result]), 200


# ─── Vue élève — mes devoirs ──────────────────────────────────────────────────

@assignments_mine_bp.route("/mine", methods=["GET"])
@jwt_required()
def get_my_assignments():
    user_id = int(get_jwt_identity())
    service = _make_service()
    result = service.get_my_assignments(user_id)
    return jsonify([a.model_dump(mode="json") for a in result]), 200


# ─── Classes Publiques & Follow ───────────────────────────────────────────────

@classes_bp.route("/public", methods=["GET"])
@jwt_required()
def get_public_classes():
    search = request.args.get("search")
    service = _make_service()
    result = service.list_public_classes(search)
    return jsonify([c.model_dump(mode="json") for c in result]), 200


@classes_bp.route("/<int:class_id>/follow", methods=["POST"])
@jwt_required()
def follow_class(class_id: int):
    user_id = int(get_jwt_identity())
    service = _make_service()
    result = service.follow_class(user_id, class_id)
    return jsonify(result.model_dump(mode="json")), 200

