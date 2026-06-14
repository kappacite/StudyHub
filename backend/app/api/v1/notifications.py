"""
Blueprint des notifications in-app (cloche).

  GET   /api/v1/notifications            → liste (?unread=1 pour non lues)
  GET   /api/v1/notifications/unread-count
  PATCH /api/v1/notifications/:id/read   → marquer comme lue
  POST  /api/v1/notifications/read-all   → tout marquer comme lu
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.dao.group_dao import GroupDAO
from app.extensions import db
from app.services.engagement_service import EngagementService

notifications_bp = Blueprint("notifications", __name__)


def _service() -> EngagementService:
    return EngagementService(group_dao=GroupDAO(db.session))


@notifications_bp.route("", methods=["GET"])
@jwt_required()
def list_notifications():
    user_id = int(get_jwt_identity())
    unread_only = request.args.get("unread") in ("1", "true", "True")
    result = _service().list_notifications(user_id, unread_only=unread_only)
    return jsonify([n.model_dump(mode="json") for n in result]), 200


@notifications_bp.route("/unread-count", methods=["GET"])
@jwt_required()
def unread_count():
    user_id = int(get_jwt_identity())
    return jsonify({"count": _service().unread_count(user_id)}), 200


@notifications_bp.route("/<int:notif_id>/read", methods=["PATCH"])
@jwt_required()
def mark_read(notif_id: int):
    user_id = int(get_jwt_identity())
    _service().mark_read(user_id, notif_id)
    return "", 204


@notifications_bp.route("/read-all", methods=["POST"])
@jwt_required()
def mark_all_read():
    user_id = int(get_jwt_identity())
    count = _service().mark_all_read(user_id)
    return jsonify({"marked": count}), 200
