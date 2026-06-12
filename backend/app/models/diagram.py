from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.search_type import TSVectorType
from app.extensions import db

class Diagram(db.Model):
    __tablename__ = "diagrams"
    __table_args__ = (
        Index('diagrams_search_idx', 'search_vector', postgresql_using='gin'),
    )

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    code = Column(Text, default="", nullable=False)  # Code Mermaid.js
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    binder_id = Column(Integer, ForeignKey("binders.id", ondelete="SET NULL"), nullable=True)
    search_vector = Column(TSVectorType, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relations
    user = relationship("User", back_populates="diagrams")
    binder = relationship("Binder", back_populates="diagrams")
    tags = relationship("Tag", secondary="diagram_tags", back_populates="diagrams")

    @property
    def binder_uuid(self) -> Optional[str]:
        return self.binder.id if self.binder else None
