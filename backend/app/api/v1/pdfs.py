from flask import Blueprint, request, jsonify, send_file, current_app, make_response
from flask_jwt_extended import get_jwt_identity
from app.extensions import db
from app.dao.pdf_dao import PDFDAO
from app.dao.binder_dao import BinderDAO
from app.services.pdf_service import PDFService
from app.middlewares.auth_middleware import jwt_required_middleware
from app.middlewares.error_handler import ValidationError
from app.api.v1.tags import remove_entity_tag, set_entity_tags
import math

pdfs_bp = Blueprint("pdfs", __name__)

pdf_dao = PDFDAO(db.session)
binder_dao = BinderDAO(db.session)
pdf_service = PDFService(pdf_dao, binder_dao)

@pdfs_bp.route("", methods=["GET"])
@jwt_required_middleware
def get_pdfs():
    user_id = int(get_jwt_identity())
    
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    
    binder_id = request.args.get("binder_id")
    if binder_id == "":
        binder_id = None
    tag_id = request.args.get("tag_id", type=int)
    
    pdfs, total = pdf_service.get_pdfs(user_id, binder_id, tag_id, page, per_page)
    pages = math.ceil(total / per_page) if total > 0 else 0
    
    return jsonify({
        "data": [p.model_dump() for p in pdfs],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": pages
        }
    }), 200

@pdfs_bp.route("", methods=["POST"])
@jwt_required_middleware
def upload_pdf():
    user_id = int(get_jwt_identity())
    
    # Vérifier la présence du fichier
    if "file" not in request.files:
        raise ValidationError("Aucun fichier fourni dans la requête (clé 'file' attendue).")
        
    file = request.files["file"]
    if file.filename == "":
        raise ValidationError("Aucun fichier sélectionné.")
        
    if not file.filename.lower().endswith(".pdf"):
        raise ValidationError("Le format de fichier doit être un PDF.")
        
    # Métadonnées
    name = request.form.get("name")
    if not name:
        name = file.filename
        
    binder_id = request.form.get("binder_id")
    if binder_id == "":
        binder_id = None
    
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    
    result = pdf_service.create_pdf(user_id, name, binder_id, file, upload_folder)
    return jsonify(result.model_dump()), 201

@pdfs_bp.route("/<pdf_id>", methods=["GET"])
@jwt_required_middleware
def get_pdf_metadata(pdf_id):
    user_id = int(get_jwt_identity())
    result = pdf_service.get_pdf(user_id, pdf_id)
    return jsonify(result.model_dump()), 200

@pdfs_bp.route("/<pdf_id>/file", methods=["GET"])
@jwt_required_middleware
def get_pdf_file(pdf_id):
    import os
    user_id = int(get_jwt_identity())
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    
    file_path = pdf_service.get_pdf_file_path(user_id, pdf_id, upload_folder)
    
    # Récupérer l'entité pour avoir le nom original
    pdf_meta = pdf_service.get_pdf(user_id, pdf_id)
    
    # Si on est en production, on utilise X-Accel-Redirect pour déléguer à Nginx
    if current_app.config.get("ENV") == "production" or os.environ.get("FLASK_ENV") == "production":
        response = make_response("")
        # Utiliser l'id dans la DB pour retrouver le fichier (pdf.filename)
        # Mais wait, pdf_meta a pdf.filename ?
        # Dans le modèle PDFDocument, le nom du fichier stocké est pdf.filename.
        # pdf_meta a le champ `filename` ? Let's check pdf_service.py or PDFResponse schema.
        # Wait, let's look at get_pdf_file_path: it uses `pdf.filename`.
        # Let's verify what fields are in PDFResponse.
        # Wait, let's look at pdf_meta. It has `filename`?
        # Let's search for `filename` or `PDFResponse` to check its schema fields.
        # But we can get it from the file_path basename! That is extremely safe and doesn't depend on the Pydantic schema structure.
        filename = os.path.basename(file_path)
        response.headers["X-Accel-Redirect"] = f"/internal_uploads/{filename}"
        response.headers["Content-Type"] = "application/pdf"
        
        from urllib.parse import quote
        try:
            filename_utf8 = quote(pdf_meta.name)
            response.headers["Content-Disposition"] = f"inline; filename*=UTF-8''{filename_utf8}"
        except Exception:
            response.headers["Content-Disposition"] = f"inline; filename={pdf_meta.name}"
        return response
    else:
        return send_file(
            file_path, 
            mimetype="application/pdf",
            as_attachment=False,
            download_name=pdf_meta.name
        )

@pdfs_bp.route("/<pdf_id>", methods=["DELETE"])
@jwt_required_middleware
def delete_pdf(pdf_id):
    user_id = int(get_jwt_identity())
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    
    pdf_service.delete_pdf(user_id, pdf_id, upload_folder)
    return "", 204


@pdfs_bp.route("/<pdf_id>/tags", methods=["POST"])
@jwt_required_middleware
def set_pdf_tags(pdf_id):
    return set_entity_tags("pdfs", pdf_id)


@pdfs_bp.route("/<pdf_id>/tags/<int:tag_id>", methods=["DELETE"])
@jwt_required_middleware
def remove_pdf_tag(pdf_id, tag_id):
    return remove_entity_tag("pdfs", pdf_id, tag_id)
