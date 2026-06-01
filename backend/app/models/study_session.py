from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.extensions import db

class StudySession(db.Model):
    __tablename__ = "study_sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    module = Column(String(50), nullable=False)  # 'flashcard', 'note', 'diagram'
    duration_seconds = Column(Integer, nullable=False, default=0)
    cards_reviewed = Column(Integer, nullable=True, default=0)
    cards_correct = Column(Integer, nullable=True, default=0)
    created_at = Column(DateTime, server_default=func.now())

    # Relations
    user = relationship("User", back_populates="study_sessions")
