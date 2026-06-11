from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.extensions import db

class Note(db.Model):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, default="", nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    binder_id = Column(Integer, ForeignKey("binders.id", ondelete="SET NULL"), nullable=True)
    is_public = Column(Boolean, default=False, nullable=False)
    share_token = Column(String(64), unique=True, nullable=True, index=True)
    last_blurting_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relations
    user = relationship("User", back_populates="notes")
    binder = relationship("Binder", back_populates="notes")
    deck = relationship("Deck", back_populates="note", uselist=False, cascade="all, delete-orphan", foreign_keys="[Deck.note_id]")
    tags = relationship("Tag", secondary="note_tags", back_populates="notes")

    @property
    def flashcards(self):
        return self.deck.cards if self.deck else []
