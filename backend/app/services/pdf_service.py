import os
import uuid
from typing import List, Tuple, Optional
from app.dao.pdf_dao import PDFDAO
from app.dao.binder_dao import BinderDAO
from app.models.pdf_document import PDFDocument
from app.schemas.pdf_schema import PDFResponse
from app.middlewares.error_handler import ResourceNotFoundError, ForbiddenError, ValidationError

class PDFService:
    def __init__(self, pdf_dao: PDFDAO, binder_dao: BinderDAO):
        self._pdf_dao = pdf_dao
        self._binder_dao = binder_dao

    def _get_pdf_or_404(self, pdf_id, user_id: int, write_required: bool = False) -> PDFDocument:
        pdf = self._pdf_dao.get_by_id(pdf_id)
        if not pdf:
            raise ResourceNotFoundError("Document PDF introuvable.")
        if pdf.user_id != user_id:
            # Accès en lecture aux PDF d'un classeur partagé (cours) ; l'écriture
            # (suppression) reste réservée selon la permission du classeur partagé.
            if pdf.binder_id:
                from app.utils.security import check_binder_access
                check_binder_access(self._pdf_dao.db, pdf.binder_id, user_id, write_required=write_required)
            else:
                raise ForbiddenError("Accès interdit à ce document PDF.")
        return pdf

    def create_pdf(
        self, 
        user_id: int, 
        name: str, 
        binder_id: Optional[int], 
        file_data, 
        upload_folder: str
    ) -> PDFResponse:
        binder_id_internal = None
        if binder_id is not None:
            binder = self._binder_dao.get_by_id(binder_id)
            if not binder or binder.user_id != user_id:
                raise ForbiddenError("Accès interdit à ce classeur.")
            binder_id_internal = binder._id
                
        # Validation du type MIME réel avec python-magic
        try:
            import magic
            header = file_data.stream.read(2048)
            file_data.stream.seek(0)
            mime_type = magic.from_buffer(header, mime=True)
            if mime_type != "application/pdf":
                raise ValidationError(f"Le fichier envoyé n'est pas un document PDF valide (Type MIME détecté : {mime_type}).")
        except ValidationError as e:
            raise e
        except Exception as e:
            # Fallback si libmagic n'est pas disponible ou s'il y a un souci système
            filename = getattr(file_data, "filename", "")
            ext = os.path.splitext(filename)[1].lower() if filename else ""
            if ext != ".pdf":
                raise ValidationError("Le fichier envoyé n'est pas un document PDF.")
                
        # Générer un nom de fichier unique sécurisé
        unique_filename = f"{uuid.uuid4().hex}.pdf"
        file_path = os.path.join(upload_folder, unique_filename)
        
        try:
            # Enregistrer le fichier sur le disque
            file_data.save(file_path)
        except Exception as e:
            raise ValidationError(f"Impossible d'enregistrer le fichier PDF : {str(e)}")
            
        pdf = PDFDocument(
            name=name,
            filename=unique_filename,
            user_id=user_id,
            binder_id=binder_id_internal
        )
        
        try:
            created = self._pdf_dao.create(pdf)
            return PDFResponse.model_validate(created)
        except Exception as e:
            # En cas d'erreur de base de données, nettoyer le fichier enregistré
            if os.path.exists(file_path):
                os.remove(file_path)
            raise e

    def get_pdfs(
        self, 
        user_id: int, 
        binder_id = None, 
        tag_id: Optional[int] = None,
        page: int = 1, 
        per_page: int = 20
    ) -> Tuple[List[PDFResponse], int]:
        offset = (page - 1) * per_page
        pdfs = self._pdf_dao.get_by_binder(user_id, binder_id, tag_id, limit=per_page, offset=offset)
        total = self._pdf_dao.count_by_binder(user_id, binder_id, tag_id)

        responses = [PDFResponse.model_validate(p) for p in pdfs]

        # Lors d'un listing global, inclure les PDF des classeurs partagés
        # (cours), en LECTURE SEULE — symétrique des notes.
        if binder_id is None and tag_id is None:
            shared_binder_ids: list = []
            for root in self._binder_dao.get_shared_root_binders(user_id):
                shared_binder_ids.append(root._id)
                shared_binder_ids.extend(d._id for d in self._binder_dao.get_descendants(root._id))
            if shared_binder_ids:
                for p in self._pdf_dao.get_by_binder_internal_ids(shared_binder_ids):
                    resp = PDFResponse.model_validate(p)
                    resp.read_only = True
                    responses.append(resp)
                total = len(responses)

        return responses, total

    def get_pdf(self, user_id: int, pdf_id) -> PDFResponse:
        pdf = self._get_pdf_or_404(pdf_id, user_id)
        resp = PDFResponse.model_validate(pdf)
        resp.read_only = pdf.user_id != user_id
        return resp

    def get_pdf_file_path(self, user_id: int, pdf_id, upload_folder: str) -> str:
        pdf = self._get_pdf_or_404(pdf_id, user_id)
        file_path = os.path.join(upload_folder, pdf.filename)
        
        if not os.path.exists(file_path):
            raise ResourceNotFoundError("Le fichier physique du PDF est introuvable sur le serveur.")
            
        return file_path

    def delete_pdf(self, user_id: int, pdf_id, upload_folder: str) -> None:
        # Écriture requise : un élève (lecture seule sur un cours partagé) ne peut pas supprimer.
        pdf = self._get_pdf_or_404(pdf_id, user_id, write_required=True)
        file_path = os.path.join(upload_folder, pdf.filename)
        
        # Supprimer d'abord de la base de données
        self._pdf_dao.delete(pdf)
        
        # Supprimer le fichier sur le disque s'il existe
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                # Log l'erreur mais ne pas faire échouer l'action API
                pass
