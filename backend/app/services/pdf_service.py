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

    def _get_pdf_or_404(self, pdf_id: int, user_id: int) -> PDFDocument:
        pdf = self._pdf_dao.get_by_id(pdf_id)
        if not pdf:
            raise ResourceNotFoundError("Document PDF introuvable.")
        if pdf.user_id != user_id:
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
        if binder_id is not None:
            binder = self._binder_dao.get_by_id(binder_id)
            if not binder or binder.user_id != user_id:
                raise ForbiddenError("Accès interdit à ce classeur.")
                
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
            binder_id=binder_id
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
        binder_id: Optional[int] = None, 
        tag_id: Optional[int] = None,
        page: int = 1, 
        per_page: int = 20
    ) -> Tuple[List[PDFResponse], int]:
        offset = (page - 1) * per_page
        pdfs = self._pdf_dao.get_by_binder(user_id, binder_id, tag_id, limit=per_page, offset=offset)
        total = self._pdf_dao.count_by_binder(user_id, binder_id, tag_id)
        
        return [PDFResponse.model_validate(p) for p in pdfs], total

    def get_pdf(self, user_id: int, pdf_id: int) -> PDFResponse:
        pdf = self._get_pdf_or_404(pdf_id, user_id)
        return PDFResponse.model_validate(pdf)

    def get_pdf_file_path(self, user_id: int, pdf_id: int, upload_folder: str) -> str:
        pdf = self._get_pdf_or_404(pdf_id, user_id)
        file_path = os.path.join(upload_folder, pdf.filename)
        
        if not os.path.exists(file_path):
            raise ResourceNotFoundError("Le fichier physique du PDF est introuvable sur le serveur.")
            
        return file_path

    def delete_pdf(self, user_id: int, pdf_id: int, upload_folder: str) -> None:
        pdf = self._get_pdf_or_404(pdf_id, user_id)
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
