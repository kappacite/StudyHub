import math
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.extensions import db
from app.dao.revision_dao import RevisionSetDAO, RevisionItemDAO
from app.dao.binder_dao import BinderDAO
from app.services.revision_service import RevisionService
from app.schemas.revision_schema import (
    RevisionSetCreate, RevisionSetUpdate,
    RevisionItemCreate, RevisionItemUpdate, RevisionItemAnswer,
    RevisionRunRequest,
)
from app.middlewares.auth_middleware import jwt_required_middleware

revision_bp = Blueprint("revision", __name__)

set_dao = RevisionSetDAO(db.session)
item_dao = RevisionItemDAO(db.session)
binder_dao = BinderDAO(db.session)
revision_service = RevisionService(set_dao, item_dao, binder_dao)


# --- Ensembles ---------------------------------------------------------------

@revision_bp.route("/sets", methods=["GET"])
@jwt_required_middleware
def get_sets():
    user_id = int(get_jwt_identity())
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    set_type = request.args.get("type", None, type=str)
    binder_id = request.args.get("binder_id", None, type=str)
    search = request.args.get("search", None, type=str)

    sets, total = revision_service.get_sets(user_id, set_type, binder_id, search, page, per_page)
    pages = math.ceil(total / per_page) if total > 0 else 0
    return jsonify({
        "data": [s.model_dump() for s in sets],
        "pagination": {"page": page, "per_page": per_page, "total": total, "pages": pages},
    }), 200


@revision_bp.route("/sets", methods=["POST"])
@jwt_required_middleware
def create_set():
    user_id = int(get_jwt_identity())
    data = RevisionSetCreate.model_validate(request.get_json() or {})
    result = revision_service.create_set(user_id, data)
    return jsonify(result.model_dump()), 201


@revision_bp.route("/sets/<int:set_id>", methods=["GET"])
@jwt_required_middleware
def get_set(set_id):
    user_id = int(get_jwt_identity())
    result = revision_service.get_set(user_id, set_id)
    return jsonify(result.model_dump()), 200


@revision_bp.route("/sets/<int:set_id>", methods=["PUT"])
@jwt_required_middleware
def update_set(set_id):
    user_id = int(get_jwt_identity())
    data = RevisionSetUpdate.model_validate(request.get_json() or {})
    result = revision_service.update_set(user_id, set_id, data)
    return jsonify(result.model_dump()), 200


@revision_bp.route("/sets/<int:set_id>", methods=["DELETE"])
@jwt_required_middleware
def delete_set(set_id):
    user_id = int(get_jwt_identity())
    revision_service.delete_set(user_id, set_id)
    return "", 204


# --- Items -------------------------------------------------------------------

@revision_bp.route("/sets/<int:set_id>/items", methods=["GET"])
@jwt_required_middleware
def get_items(set_id):
    user_id = int(get_jwt_identity())
    items = revision_service.get_items(user_id, set_id)
    return jsonify({"data": [i.model_dump() for i in items]}), 200


@revision_bp.route("/sets/<int:set_id>/items", methods=["POST"])
@jwt_required_middleware
def create_item(set_id):
    user_id = int(get_jwt_identity())
    data = RevisionItemCreate.model_validate(request.get_json() or {})
    result = revision_service.create_item(user_id, set_id, data)
    return jsonify(result.model_dump()), 201


@revision_bp.route("/sets/<int:set_id>/items/<int:item_id>", methods=["PUT"])
@jwt_required_middleware
def update_item(set_id, item_id):
    user_id = int(get_jwt_identity())
    data = RevisionItemUpdate.model_validate(request.get_json() or {})
    result = revision_service.update_item(user_id, set_id, item_id, data)
    return jsonify(result.model_dump()), 200


@revision_bp.route("/sets/<int:set_id>/items/<int:item_id>", methods=["DELETE"])
@jwt_required_middleware
def delete_item(set_id, item_id):
    user_id = int(get_jwt_identity())
    revision_service.delete_item(user_id, set_id, item_id)
    return "", 204


# --- Étude (SM-2) ------------------------------------------------------------

@revision_bp.route("/sets/<int:set_id>/study", methods=["GET"])
@jwt_required_middleware
def study_set(set_id):
    user_id = int(get_jwt_identity())
    items = revision_service.get_study_items(user_id, set_id)
    return jsonify([i.model_dump() for i in items]), 200


@revision_bp.route("/sets/<int:set_id>/study/answer/<int:item_id>", methods=["POST"])
@jwt_required_middleware
def answer_item(set_id, item_id):
    user_id = int(get_jwt_identity())
    data = RevisionItemAnswer.model_validate(request.get_json() or {})
    result = revision_service.answer_item(user_id, set_id, item_id, data.score)
    return jsonify(result.model_dump()), 200


@revision_bp.route("/sets/<int:set_id>/run", methods=["POST"])
@jwt_required_middleware
def run_qcm(set_id):
    user_id = int(get_jwt_identity())
    data = RevisionRunRequest.model_validate(request.get_json() or {})
    result = revision_service.run_qcm(user_id, set_id, data)
    return jsonify(result.model_dump()), 200
