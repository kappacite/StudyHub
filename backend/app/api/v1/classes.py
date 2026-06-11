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
from app.extensions import db
from app.schemas.class_schema import ClassCreateSchema, AssignmentCreateSchema
from app.services.class_service import ClassService
from app.middlewares.error_handler import ValidationError

classes_bp = Blueprint("classes", __name__)
assignments_mine_bp = Blueprint("assignments_mine", __name__)


def _make_service() -> ClassService:
    return ClassService(
        group_dao=GroupDAO(db.session),
        binder_dao=BinderDAO(db.session),
        user_dao=UserDAO(db.session)
    )


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

