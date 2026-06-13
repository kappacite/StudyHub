from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.extensions import db


class HiddenNote(db.Model):
    """Note (partagée par un cours) masquée par un utilisateur dans sa propre vue.
    Permet à un élève de cacher une note du prof (ex. après en avoir fait une copie)."""
    __tablename__ = "hidden_notes"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    # Référence l'id interne de la note (colonne notes.id).
    note_id = Column(Integer, ForeignKey("notes.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime, server_default=func.now())
