from sqlalchemy import Column, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.extensions import db


class ClassInsight(db.Model):
    """Cache de la dernière analyse de lacunes (data + résumé IA) d'une classe.

    Recalculée à la demande (tâche Celery) et conservée pour éviter de rappeler
    l'IA à chaque consultation du tableau de bord professeur.
    """
    __tablename__ = "class_insights"

    id         = Column(Integer, primary_key=True)
    group_id   = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False, index=True)
    payload    = Column(JSON, nullable=False)   # {"weak_topics": [...], "summary": "...", "ai": bool}
    created_at = Column(DateTime, server_default=func.now())

    group = relationship("Group")
