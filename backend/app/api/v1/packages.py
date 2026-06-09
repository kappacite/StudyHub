from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.services.community_service import CommunityService
from app.middlewares.auth_middleware import jwt_required_middleware
import math

packages_bp = Blueprint("packages", __name__)
community_service = CommunityService()

@packages_bp.route("", methods=["GET"])
def get_public_packages():
    # Route publique d'exploration des packages
    search = request.args.get("search")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    
    binders, total = community_service.list_public_packages(search, page, per_page)
    pages = math.ceil(total / per_page) if total > 0 else 0
    
    return jsonify({
        "data": [b.model_dump() for b in binders],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": pages
        }
    }), 200

@packages_bp.route("/<int:binder_id>", methods=["GET"])
def get_public_package(binder_id):
    from app.models.binder import Binder
    from app.schemas.binder_schema import BinderResponse
    from app.extensions import db
    
    binder = db.session.query(Binder).filter(Binder.id == binder_id, Binder.is_public == True).first()
    if not binder:
        return jsonify({
            "error": {
                "code": "RESOURCE_NOT_FOUND",
                "message": "Le package demandé n'existe pas ou n'est pas public."
            }
        }), 404
        
    notes = []
    decks = []
    diagrams = []
    pdfs = []
    
    def collect_contents(b):
        for n in b.notes:
            notes.append(n.title)
        for d in b.decks:
            if d.note_id is None:
                decks.append(d.name)
        for diag in b.diagrams:
            diagrams.append(diag.title)
        for pdf in b.pdfs:
            pdfs.append(pdf.filename)
            
        for child in b.children:
            collect_contents(child)
            
    collect_contents(binder)
    
    return jsonify({
        "binder": BinderResponse.model_validate(binder).model_dump(),
        "notes": notes,
        "decks": decks,
        "diagrams": diagrams,
        "pdfs": pdfs
    }), 200

@packages_bp.route("/<int:binder_id>/clone", methods=["POST"])
@jwt_required_middleware
def clone_package(binder_id):
    user_id = int(get_jwt_identity())
    result = community_service.clone_package(user_id, binder_id)
    return jsonify(result.model_dump()), 201
