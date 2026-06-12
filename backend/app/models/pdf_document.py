from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.extensions import db
from typing import Optional
import uuid

class PDFDocument(db.Model):
    __tablename__ = "pdf_documents"

    _id = Column("id", Integer, primary_key=True)
    id = Column("uuid", String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False)
    filename = Column(String(255), nullable=False)  # Nom de fichier unique généré sur le disque
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    binder_id = Column(Integer, ForeignKey("binders.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relations
    user = relationship("User", back_populates="pdfs")
    binder = relationship("Binder", back_populates="pdfs")
    tags = relationship("Tag", secondary="pdf_tags", back_populates="pdfs")

    @property
    def binder_uuid(self) -> Optional[str]:
        return self.binder.id if self.binder else None
