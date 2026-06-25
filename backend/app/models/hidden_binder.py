from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.extensions import db


class HiddenBinder(db.Model):
    """Classeur (partagé par un cours/groupe) masqué par un utilisateur dans sa
    propre vue. Permet à un destinataire de retirer un classeur partagé de son
    arborescence SANS supprimer l'original (qui appartient à un autre utilisateur)."""
    __tablename__ = "hidden_binders"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    # Référence l'id interne du classeur (colonne binders.id).
    binder_id = Column(Integer, ForeignKey("binders.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime, server_default=func.now())
