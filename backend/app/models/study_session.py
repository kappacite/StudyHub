from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.extensions import db

class StudySession(db.Model):
    __tablename__ = "study_sessions"
    __table_args__ = (
        # Couvre le filtrage par user ET les plages de dates (heatmap, streak).
        Index('ix_study_sessions_user_id_created_at', 'user_id', 'created_at'),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    module = Column(String(50), nullable=False)  # 'flashcard', 'note', 'diagram'
    duration_seconds = Column(Integer, nullable=False, default=0)
    cards_reviewed = Column(Integer, nullable=True, default=0)
    cards_correct = Column(Integer, nullable=True, default=0)
    
    # Pour le suivi des flashcards individuelles
    flashcard_id = Column(Integer, ForeignKey("flashcards.id", ondelete="CASCADE"), nullable=True)
    grade = Column(Integer, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())

    # Relations
    user = relationship("User", back_populates="study_sessions")
    flashcard = relationship("Flashcard")

from sqlalchemy import event
from app.utils.cache import invalidate_stats_cache

@event.listens_for(StudySession, 'after_insert')
def after_insert_session(mapper, connection, target):
    invalidate_stats_cache(target.user_id)

@event.listens_for(StudySession, 'after_update')
def after_update_session(mapper, connection, target):
    invalidate_stats_cache(target.user_id)

@event.listens_for(StudySession, 'after_delete')
def after_delete_session(mapper, connection, target):
    invalidate_stats_cache(target.user_id)
