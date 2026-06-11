from sqlalchemy import Column, Integer, Float, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.extensions import db

class Quiz(db.Model):
    __tablename__ = "quizzes"
    
    id = Column(Integer, primary_key=True)
    note_id = Column(Integer, ForeignKey("notes.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    score_pct = Column(Float, nullable=True)   # null = non complété
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)

    # Relations
    note = relationship("Note")
    user = relationship("User")
    questions = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete-orphan")

class QuizQuestion(db.Model):
    __tablename__ = "quiz_questions"
    
    id = Column(Integer, primary_key=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    question_text = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)  # [{"id": "a", "text": "...", "correct": bool}]
    user_answer_id = Column(String(1), nullable=True)  # "a", "b", "c", "d"

    # Relations
    quiz = relationship("Quiz", back_populates="questions")
