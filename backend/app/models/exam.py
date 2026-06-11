from sqlalchemy import Column, Integer, Float, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.extensions import db

class ExamSession(db.Model):
    __tablename__ = "exam_sessions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    binder_id = Column(Integer, ForeignKey("binders.id", ondelete="SET NULL"), nullable=True)
    duration_seconds = Column(Integer, nullable=False)
    started_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
    score_pct = Column(Float, nullable=True)
    flashcard_score = Column(Float, nullable=True)
    qcm_score = Column(Float, nullable=True)
    time_taken_seconds = Column(Integer, nullable=True)
    items_snapshot = Column(JSON, nullable=False)  # [{id, item_type, item_id, front, back, options: [{"id", "text"}], user_answer, is_correct}]

    # Relations
    user = relationship("User")
    binder = relationship("Binder")
