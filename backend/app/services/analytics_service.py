"""
AnalyticsService — tableau de bord agrégé du professeur.

Toutes les métriques sont calculées par requêtes ensemblistes (GROUP BY / agrégats)
à nombre de requêtes borné, indépendamment du nombre d'élèves ou de devoirs — pour
éviter le N+1 de l'ancien `get_class_materials_progress`.
"""
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import func, case

from app.dao.group_dao import GroupDAO
from app.extensions import db
from app.models.group import Group, GroupMember
from app.models.assignment import Assignment, AssignmentProgress
from app.models.study_session import StudySession
from app.models.evaluation import Evaluation, EvaluationItem
from app.models.note import Note
from app.models.user import User
from app.schemas.analytics_schema import (
    ClassOverviewSchema, AssignmentStatSchema, WeakTopicSchema, StudentStatSchema,
)
from app.middlewares.error_handler import ResourceNotFoundError, ForbiddenError


class AnalyticsService:
    def __init__(self, group_dao: GroupDAO):
        self._group_dao = group_dao
        self._db = group_dao.db

    def _require_teacher(self, class_id: int, user_id: int) -> Group:
        group = self._group_dao.get_by_id(class_id)
        if not group or not group.is_class:
            raise ResourceNotFoundError("Classe introuvable.")
        member = self._group_dao.get_group_member(class_id, user_id)
        if not member or member.role not in ("owner", "admin"):
            raise ForbiddenError("Action réservée au professeur.")
        return group

    def _student_ids(self, class_id: int) -> List[int]:
        rows = (
            self._db.query(GroupMember.user_id)
            .filter(GroupMember.group_id == class_id,
                    GroupMember.role.notin_(("owner", "admin")))
            .all()
        )
        return [r[0] for r in rows]

    # ─────────────────────────────────────────────────────────────────────────
    # Vue d'ensemble
    # ─────────────────────────────────────────────────────────────────────────

    def get_class_overview(self, class_id: int, user_id: int) -> ClassOverviewSchema:
        self._require_teacher(class_id, user_id)
        student_ids = self._student_ids(class_id)

        # Devoirs de la classe (1 requête).
        assignments = (
            self._db.query(Assignment.id, Assignment.title, Assignment.due_date)
            .filter(Assignment.group_id == class_id)
            .all()
        )
        assignment_ids = [a.id for a in assignments]

        # Agrégat par devoir : nb soumissions, complétées, score moyen (1 requête).
        per_asgn = {}
        if assignment_ids:
            rows = (
                self._db.query(
                    AssignmentProgress.assignment_id,
                    func.count(AssignmentProgress.user_id),
                    func.sum(case((AssignmentProgress.completed_at.isnot(None), 1), else_=0)),
                    func.avg(AssignmentProgress.score_pct),
                )
                .filter(AssignmentProgress.assignment_id.in_(assignment_ids))
                .group_by(AssignmentProgress.assignment_id)
                .all()
            )
            per_asgn = {r[0]: (r[1] or 0, r[2] or 0, r[3]) for r in rows}

        assignment_stats: List[AssignmentStatSchema] = []
        total_subs = total_completed = 0
        score_sum = 0.0
        score_n = 0
        for a in assignments:
            subs, completed, avg = per_asgn.get(a.id, (0, 0, None))
            total_subs += subs
            total_completed += completed
            if avg is not None:
                score_sum += float(avg)
                score_n += 1
            assignment_stats.append(AssignmentStatSchema(
                id=a.id, title=a.title, due_date=a.due_date,
                submissions_count=subs, completed_count=completed,
                completion_rate=(completed / subs * 100.0) if subs else 0.0,
                avg_score=float(avg) if avg is not None else None,
            ))

        completion_rate = (total_completed / total_subs * 100.0) if total_subs else 0.0
        avg_score = (score_sum / score_n) if score_n else None

        # Élèves actifs (≥1 session d'étude sur 7 jours) — 1 requête.
        active_7d = 0
        if student_ids:
            since = datetime.utcnow() - timedelta(days=7)
            active_7d = (
                self._db.query(func.count(func.distinct(StudySession.user_id)))
                .filter(StudySession.user_id.in_(student_ids),
                        StudySession.created_at >= since)
                .scalar()
            ) or 0

        # B5 — Stats de révision & avancement par élève (agrégats bornés).
        student_stats: List[StudentStatSchema] = []
        avg_study_minutes = 0.0
        study_success_rate: Optional[float] = None
        if student_ids:
            # Noms (1 requête).
            names = dict(
                self._db.query(User.id, User.username)
                .filter(User.id.in_(student_ids)).all()
            )
            # Temps d'étude + cartes par élève (1 requête).
            study_rows = (
                self._db.query(
                    StudySession.user_id,
                    func.sum(StudySession.duration_seconds),
                    func.sum(StudySession.cards_reviewed),
                    func.sum(StudySession.cards_correct),
                )
                .filter(StudySession.user_id.in_(student_ids))
                .group_by(StudySession.user_id)
                .all()
            )
            study_by_user = {r[0]: (r[1] or 0, r[2] or 0, r[3] or 0) for r in study_rows}
            # Devoirs terminés + score moyen par élève (1 requête).
            prog_by_user = {}
            if assignment_ids:
                prog_rows = (
                    self._db.query(
                        AssignmentProgress.user_id,
                        func.sum(case((AssignmentProgress.completed_at.isnot(None), 1), else_=0)),
                        func.avg(AssignmentProgress.score_pct),
                    )
                    .filter(AssignmentProgress.assignment_id.in_(assignment_ids))
                    .group_by(AssignmentProgress.user_id)
                    .all()
                )
                prog_by_user = {r[0]: (r[1] or 0, r[2]) for r in prog_rows}

            total_seconds = 0
            total_reviewed = 0
            total_correct = 0
            for sid in student_ids:
                secs, reviewed, correct = study_by_user.get(sid, (0, 0, 0))
                completed, avg = prog_by_user.get(sid, (0, None))
                total_seconds += secs
                total_reviewed += reviewed
                total_correct += correct
                student_stats.append(StudentStatSchema(
                    user_id=sid,
                    username=names.get(sid, f"#{sid}"),
                    completed_assignments=int(completed),
                    avg_score=float(avg) if avg is not None else None,
                    study_minutes=round(secs / 60),
                    success_rate=(correct / reviewed * 100.0) if reviewed else None,
                ))
            student_stats.sort(key=lambda s: s.completed_assignments, reverse=True)
            avg_study_minutes = round(total_seconds / 60 / len(student_ids), 1)
            study_success_rate = (total_correct / total_reviewed * 100.0) if total_reviewed else None

        return ClassOverviewSchema(
            class_id=class_id,
            students_count=len(student_ids),
            assignments_count=len(assignments),
            completion_rate=completion_rate,
            avg_score=avg_score,
            active_students_7d=active_7d,
            avg_study_minutes=avg_study_minutes,
            study_success_rate=study_success_rate,
            assignments=assignment_stats,
            students=student_stats,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Lacunes de la classe (data-driven, enrichissable par IA)
    # ─────────────────────────────────────────────────────────────────────────

    def compute_weak_topics(self, class_id: int, limit: int = 8) -> List[WeakTopicSchema]:
        """Notes où les élèves se trompent le plus (depuis les items d'évaluation)."""
        student_ids = self._student_ids(class_id)
        if not student_ids:
            return []

        rows = (
            self._db.query(
                Evaluation.note_id,
                func.count(EvaluationItem.id),
                func.sum(case((EvaluationItem.is_correct.is_(False), 1), else_=0)),
            )
            .join(EvaluationItem, EvaluationItem.evaluation_id == Evaluation.id)
            .filter(Evaluation.user_id.in_(student_ids),
                    EvaluationItem.is_correct.isnot(None))
            .group_by(Evaluation.note_id)
            .all()
        )
        if not rows:
            return []

        note_ids = [r[0] for r in rows]
        titles = dict(
            self._db.query(Note._id, Note.title)
            .filter(Note._id.in_(note_ids))
            .all()
        )

        topics = []
        for note_id, sample, wrong in rows:
            sample = sample or 0
            wrong = wrong or 0
            if sample == 0:
                continue
            topics.append(WeakTopicSchema(
                note_id=note_id,
                note_title=titles.get(note_id, f"Note #{note_id}"),
                error_rate=wrong / sample * 100.0,
                sample=sample,
            ))
        topics.sort(key=lambda t: t.error_rate, reverse=True)
        return topics[:limit]

    @staticmethod
    def heuristic_summary(weak_topics: List[WeakTopicSchema]) -> str:
        if not weak_topics:
            return "Pas encore assez de données d'évaluation pour identifier des lacunes."
        worst = weak_topics[0]
        names = ", ".join(t.note_title for t in weak_topics[:3])
        return (
            f"La classe rencontre le plus de difficultés sur « {worst.note_title} » "
            f"({round(worst.error_rate)}% d'erreurs). Notions à retravailler en priorité : {names}."
        )
