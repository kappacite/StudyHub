"""
AssignmentDAO — accès données pour les devoirs et leurs tâches polymorphes.

Aucune logique métier ici : uniquement des requêtes SQLAlchemy. Centralise les
accès aux tables assignments / assignment_tasks / assignment_task_progress /
assignment_progress, qui étaient auparavant dispersés (et inline) dans
ClassService — en violation de la séparation des couches.
"""
from typing import List, Optional
from sqlalchemy.orm import Session, selectinload

from app.dao.base_dao import BaseDAO
from app.models.assignment import (
    Assignment, AssignmentTask, AssignmentTaskProgress, AssignmentProgress,
)


class AssignmentDAO(BaseDAO[Assignment]):
    def __init__(self, db: Session):
        super().__init__(Assignment, db)

    # ─── Assignments ────────────────────────────────────────────────────────────

    def get_assignment(self, assignment_id: int) -> Optional[Assignment]:
        return self.db.get(Assignment, assignment_id)

    def get_assignment_with_tasks(self, assignment_id: int) -> Optional[Assignment]:
        return (
            self.db.query(Assignment)
            .options(selectinload(Assignment.tasks))
            .filter(Assignment.id == assignment_id)
            .first()
        )

    def list_by_class(self, group_id: int) -> List[Assignment]:
        return (
            self.db.query(Assignment)
            .filter(Assignment.group_id == group_id)
            .order_by(Assignment.due_date)
            .all()
        )

    def list_by_class_with_tasks(self, group_id: int) -> List[Assignment]:
        return (
            self.db.query(Assignment)
            .options(selectinload(Assignment.tasks))
            .filter(Assignment.group_id == group_id)
            .order_by(Assignment.due_date)
            .all()
        )

    def add_assignment(self, assignment: Assignment) -> Assignment:
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)
        return assignment

    def delete_assignment(self, assignment: Assignment) -> None:
        self.db.delete(assignment)
        self.db.commit()

    # ─── Tasks ──────────────────────────────────────────────────────────────────

    def add_task(self, task: AssignmentTask, commit: bool = True) -> AssignmentTask:
        self.db.add(task)
        if commit:
            self.db.commit()
            self.db.refresh(task)
        return task

    def get_task(self, task_id: int) -> Optional[AssignmentTask]:
        return self.db.get(AssignmentTask, task_id)

    def list_tasks(self, assignment_id: int) -> List[AssignmentTask]:
        return (
            self.db.query(AssignmentTask)
            .filter(AssignmentTask.assignment_id == assignment_id)
            .order_by(AssignmentTask.order)
            .all()
        )

    # ─── Task progress ──────────────────────────────────────────────────────────

    def get_task_progress(self, task_id: int, user_id: int) -> Optional[AssignmentTaskProgress]:
        return self.db.get(AssignmentTaskProgress, (task_id, user_id))

    def list_task_progress_for_user(self, assignment_id: int, user_id: int) -> List[AssignmentTaskProgress]:
        return (
            self.db.query(AssignmentTaskProgress)
            .join(AssignmentTask, AssignmentTaskProgress.task_id == AssignmentTask.id)
            .filter(
                AssignmentTask.assignment_id == assignment_id,
                AssignmentTaskProgress.user_id == user_id,
            )
            .all()
        )

    def upsert_task_progress(
        self, task_id: int, user_id: int, commit: bool = True
    ) -> AssignmentTaskProgress:
        prog = self.db.get(AssignmentTaskProgress, (task_id, user_id))
        if not prog:
            prog = AssignmentTaskProgress(task_id=task_id, user_id=user_id)
            self.db.add(prog)
        if commit:
            self.db.commit()
            self.db.refresh(prog)
        return prog

    # ─── Submission aggregate (assignment_progress) ─────────────────────────────

    def get_submission(self, assignment_id: int, user_id: int) -> Optional[AssignmentProgress]:
        return self.db.get(AssignmentProgress, (assignment_id, user_id))

    def upsert_submission(
        self, assignment_id: int, user_id: int, commit: bool = True
    ) -> AssignmentProgress:
        sub = self.db.get(AssignmentProgress, (assignment_id, user_id))
        if not sub:
            sub = AssignmentProgress(assignment_id=assignment_id, user_id=user_id)
            self.db.add(sub)
        if commit:
            self.db.commit()
            self.db.refresh(sub)
        return sub

    def list_submissions(self, assignment_id: int) -> List[AssignmentProgress]:
        return (
            self.db.query(AssignmentProgress)
            .filter(AssignmentProgress.assignment_id == assignment_id)
            .all()
        )
