from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.extensions import db


# Types de tâches supportés par un devoir.
# 'revision' cible un ensemble de révision typé (qcm/vf/association/définition/ordre).
TASK_TYPES = ("flashcards", "quiz", "exam", "blurting", "read", "revision")


class Assignment(db.Model):
    __tablename__ = "assignments"

    id          = Column(Integer, primary_key=True)
    group_id    = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    # binder_id reste pour la rétro-compatibilité (devoir « mono-classeur » historique).
    # Nullable depuis la refonte multi-tâches : un devoir peut n'avoir que des tâches typées.
    binder_id   = Column(Integer, ForeignKey("binders.id", ondelete="CASCADE"), nullable=True)
    title       = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    instructions = Column(Text, nullable=True)
    due_date    = Column(DateTime, nullable=True)
    publish_at  = Column(DateTime, nullable=True)              # publication programmée (null = immédiat)
    allow_late  = Column(Boolean, default=True, nullable=False)
    created_by  = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at  = Column(DateTime, server_default=func.now())

    # Relations
    group      = relationship("Group", back_populates="assignments")
    binder     = relationship("Binder")
    creator    = relationship("User", foreign_keys=[created_by])
    tasks      = relationship(
        "AssignmentTask",
        back_populates="assignment",
        cascade="all, delete-orphan",
        order_by="AssignmentTask.order",
    )
    progresses = relationship("AssignmentProgress", back_populates="assignment", cascade="all, delete-orphan")


class AssignmentTask(db.Model):
    """Une tâche polymorphe d'un devoir (flashcards, QCM, examen, blurting, lecture)."""
    __tablename__ = "assignment_tasks"

    id            = Column(Integer, primary_key=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False, index=True)
    task_type     = Column(String(20), nullable=False)        # cf. TASK_TYPES
    # Référence polymorphe vers la cible (PK interne entier) — pas de FK car multi-tables.
    ref_id        = Column(Integer, nullable=True)            # deck.id / note._id / binder._id / pdf._id
    ref_uuid      = Column(String(36), nullable=True)         # UUID public si la cible en possède un
    ref_label     = Column(String(200), nullable=True)        # nom dénormalisé pour l'affichage
    goal          = Column(JSON, nullable=True)               # {"min_cards": 20, "min_score": 80, ...}
    order         = Column(Integer, default=0, nullable=False)

    # Relations
    assignment = relationship("Assignment", back_populates="tasks")
    progresses = relationship(
        "AssignmentTaskProgress",
        back_populates="task",
        cascade="all, delete-orphan",
    )


class AssignmentTaskProgress(db.Model):
    """Progression d'un élève sur une tâche précise."""
    __tablename__ = "assignment_task_progress"

    task_id       = Column(Integer, ForeignKey("assignment_tasks.id", ondelete="CASCADE"), primary_key=True)
    user_id       = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    status        = Column(String(12), default="todo", nullable=False)   # "todo" | "in_progress" | "done"
    score_pct     = Column(Float, nullable=True)
    attempts      = Column(Integer, default=0, nullable=False)
    submitted_at  = Column(DateTime, nullable=True)
    completed_at  = Column(DateTime, nullable=True)
    payload       = Column(JSON, nullable=True)              # {"cards_reviewed": int, "total_cards": int, ...}

    # Relations
    task = relationship("AssignmentTask", back_populates="progresses")
    user = relationship("User")


class AssignmentProgress(db.Model):
    """
    Agrégat de progression d'un élève pour un devoir (= « soumission »).

    Conserve les colonnes historiques (cards_reviewed/score_pct/completed_at) pour la
    rétro-compatibilité du flux mono-classeur. La refonte multi-tâches recalcule cet
    agrégat à partir des AssignmentTaskProgress.
    """
    __tablename__ = "assignment_progress"

    assignment_id  = Column(Integer, ForeignKey("assignments.id", ondelete="CASCADE"), primary_key=True)
    user_id        = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    cards_reviewed = Column(Integer, default=0, nullable=False)
    score_pct      = Column(Float, nullable=True)
    completed_at   = Column(DateTime, nullable=True)
    # Notation manuelle par le professeur (optionnelle, complète le score auto)
    teacher_score    = Column(Float, nullable=True)
    teacher_feedback = Column(Text, nullable=True)
    graded_by        = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    graded_at        = Column(DateTime, nullable=True)

    # Relations
    assignment = relationship("Assignment", back_populates="progresses")
    user       = relationship("User", foreign_keys=[user_id])
