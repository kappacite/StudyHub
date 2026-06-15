from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.extensions import db
from app.dao.group_dao import GroupDAO
from app.dao.binder_dao import BinderDAO
from app.dao.user_dao import UserDAO
from app.services.group_service import GroupService
from app.schemas.group_schema import (
    GroupCreateSchema, GroupJoinSchema, GroupBinderShareSchema,
    GroupMemberRoleUpdateSchema, GroupResponseSchema, GroupDetailResponseSchema,
    GroupMemberResponseSchema, GroupBinderResponseSchema, GroupActivityResponseSchema,
    GroupMemberProgressSchema
)
from app.middlewares.auth_middleware import jwt_required_middleware

groups_bp = Blueprint("groups", __name__)

# Initialisation des DAOs
group_dao = GroupDAO(db.session)
binder_dao = BinderDAO(db.session)
user_dao = UserDAO(db.session)

# Initialisation du service
group_service = GroupService(
    group_dao=group_dao,
    binder_dao=binder_dao,
    user_dao=user_dao
)

@groups_bp.route("", methods=["POST"])
@jwt_required_middleware
def create_group():
    user_id = int(get_jwt_identity())
    data_dict = request.get_json() or {}
    
    req_data = GroupCreateSchema.model_validate(data_dict)
    group = group_service.create_group(user_id=user_id, data=req_data)
    
    return jsonify(group.model_dump()), 201

@groups_bp.route("", methods=["GET"])
@jwt_required_middleware
def get_my_groups():
    user_id = int(get_jwt_identity())
    groups = group_service.get_my_groups(user_id=user_id)
    
    return jsonify([g.model_dump() for g in groups]), 200

@groups_bp.route("/<int:group_id>", methods=["GET"])
@jwt_required_middleware
def get_group_detail(group_id):
    user_id = int(get_jwt_identity())
    group_detail = group_service.get_group_detail(group_id=group_id, user_id=user_id)
    
    return jsonify(group_detail.model_dump()), 200

@groups_bp.route("/join", methods=["POST"])
@jwt_required_middleware
def join_group():
    user_id = int(get_jwt_identity())
    data_dict = request.get_json() or {}
    
    req_data = GroupJoinSchema.model_validate(data_dict)
    group = group_service.join_group(user_id=user_id, invite_code=req_data.invite_code)
    
    return jsonify(group.model_dump()), 200

@groups_bp.route("/<int:group_id>/members/<int:target_user_id>", methods=["DELETE"])
@jwt_required_middleware
def leave_or_exclude_member(group_id, target_user_id):
    user_id = int(get_jwt_identity())
    group_service.leave_or_exclude_member(
        group_id=group_id,
        target_user_id=target_user_id,
        request_user_id=user_id
    )
    
    return "", 204

@groups_bp.route("/<int:group_id>/members/<int:target_user_id>", methods=["PATCH"])
@jwt_required_middleware
def update_member_role(group_id, target_user_id):
    user_id = int(get_jwt_identity())
    data_dict = request.get_json() or {}
    
    req_data = GroupMemberRoleUpdateSchema.model_validate(data_dict)
    updated_member = group_service.update_member_role(
        group_id=group_id,
        target_user_id=target_user_id,
        request_user_id=user_id,
        new_role=req_data.role
    )
    
    return jsonify(updated_member.model_dump()), 200

@groups_bp.route("/<int:group_id>/binders", methods=["POST"])
@jwt_required_middleware
def share_binder(group_id):
    user_id = int(get_jwt_identity())
    data_dict = request.get_json() or {}
    
    req_data = GroupBinderShareSchema.model_validate(data_dict)
    shared_binder = group_service.share_binder(
        group_id=group_id,
        user_id=user_id,
        binder_id=req_data.binder_id,
        permission=req_data.permission
    )
    
    return jsonify(shared_binder.model_dump()), 200

@groups_bp.route("/binders/<string:binder_id>/classes", methods=["GET"])
@jwt_required_middleware
def get_binder_classes(binder_id):
    user_id = int(get_jwt_identity())
    classes = group_service.get_classes_sharing_binder(user_id, binder_id)
    return jsonify([c.model_dump() for c in classes]), 200

@groups_bp.route("/<int:group_id>/binders/<string:binder_id>", methods=["DELETE"])
@jwt_required_middleware
def unshare_binder(group_id, binder_id):
    user_id = int(get_jwt_identity())
    group_service.unshare_binder(
        group_id=group_id,
        user_id=user_id,
        binder_id=binder_id
    )
    
    return "", 204

@groups_bp.route("/<int:group_id>/activity", methods=["GET"])
@jwt_required_middleware
def get_group_activity(group_id):
    user_id = int(get_jwt_identity())
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    
    activities = group_service.get_group_activity(
        group_id=group_id,
        user_id=user_id,
        page=page,
        per_page=per_page
    )
    
    return jsonify([act.model_dump() for act in activities]), 200

@groups_bp.route("/<int:group_id>/members/progress", methods=["GET"])
@jwt_required_middleware
def get_group_members_progress(group_id):
    user_id = int(get_jwt_identity())
    progress = group_service.get_group_members_progress(
        group_id=group_id,
        user_id=user_id
    )
    
    return jsonify([p.model_dump() for p in progress]), 200
