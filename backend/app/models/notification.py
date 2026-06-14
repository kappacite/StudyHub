from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.extensions import db


class Notification(db.Model):
    """Notification in-app (cloche). Générée côté serveur (nouveau devoir, deadline…)."""
    __tablename__ = "notifications"

    id         = Column(Integer, primary_key=True)
    user_id    = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type       = Column(String(30), nullable=False)   # "new_assignment" | "announcement" | "due_soon" | ...
    title      = Column(String(200), nullable=False)
    body       = Column(Text, nullable=True)
    link       = Column(String(255), nullable=True)    # route applicative cible
    group_id   = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=True)
    read_at    = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)

    user = relationship("User")
