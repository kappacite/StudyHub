from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.extensions import db


class Assignment(db.Model):
    __tablename__ = "assignments"

    id          = Column(Integer, primary_key=True)
    group_id    = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    binder_id   = Column(Integer, ForeignKey("binders.id", ondelete="CASCADE"), nullable=False)
    title       = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    due_date    = Column(DateTime, nullable=True)
    created_by  = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at  = Column(DateTime, server_default=func.now())

    # Relations
    group      = relationship("Group", back_populates="assignments")
    binder     = relationship("Binder")
    creator    = relationship("User", foreign_keys=[created_by])
    progresses = relationship("AssignmentProgress", back_populates="assignment", cascade="all, delete-orphan")


class AssignmentProgress(db.Model):
    __tablename__ = "assignment_progress"

    assignment_id = Column(Integer, ForeignKey("assignments.id", ondelete="CASCADE"), primary_key=True)
    user_id       = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    cards_reviewed = Column(Integer, default=0, nullable=False)
    score_pct     = Column(Float, nullable=True)
    completed_at  = Column(DateTime, nullable=True)

    # Relations
    assignment = relationship("Assignment", back_populates="progresses")
    user       = relationship("User")
