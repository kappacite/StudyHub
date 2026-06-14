"""
EngagementService — fil d'actualité, classement, badges et notifications de classe.

Métriques calculées par requêtes bornées (pas de N+1).
"""
from datetime import datetime, timedelta, date
from typing import List, Optional

from sqlalchemy import func, case

from app.dao.group_dao import GroupDAO
from app.models.group import Group, GroupMember, GroupActivity
from app.models.assignment import Assignment, AssignmentProgress
from app.models.study_session import StudySession
from app.models.notification import Notification
from app.models.user import User
from app.schemas.engagement_schema import (
    AnnouncementCreateSchema, FeedItemSchema,
    LeaderboardSchema, LeaderboardEntrySchema, NotificationSchema,
)
from app.middlewares.error_handler import ResourceNotFoundError, ForbiddenError


class EngagementService:
    def __init__(self, group_dao: GroupDAO):
        self._group_dao = group_dao
        self._db = group_dao.db

    # ─── Helpers ──────────────────────────────────────────────────────────────

    def _get_class_or_404(self, class_id: int) -> Group:
        g = self._group_dao.get_by_id(class_id)
        if not g or not g.is_class:
            raise ResourceNotFoundError("Classe introuvable.")
        return g

    def _require_membership(self, class_id: int, user_id: int) -> GroupMember:
        m = self._group_dao.get_group_member(class_id, user_id)
        if not m:
            raise ForbiddenError("Vous n'êtes pas membre de cette classe.")
        return m

    def _require_teacher(self, class_id: int, user_id: int) -> GroupMember:
        m = self._require_membership(class_id, user_id)
        if m.role not in ("owner", "admin"):
            raise ForbiddenError("Action réservée au professeur.")
        return m

    def _student_ids(self, class_id: int) -> List[int]:
        rows = (
            self._db.query(GroupMember.user_id)
            .filter(GroupMember.group_id == class_id,
                    GroupMember.role.notin_(("owner", "admin")))
            .all()
        )
        return [r[0] for r in rows]

    # ─── Annonces & fil ─────────────────────────────────────────────────────────

    def post_announcement(
        self, class_id: int, teacher_id: int, data: AnnouncementCreateSchema
    ) -> FeedItemSchema:
        self._get_class_or_404(class_id)
        self._require_teacher(class_id, teacher_id)

        payload = {"title": data.title, "body": data.body}
        activity = self._group_dao.add_group_activity(class_id, teacher_id, "announcement", payload)

        # Notifier les élèves.
        self.create_notifications_for_students(
            class_id, exclude_user_id=teacher_id, ntype="announcement",
            title=data.title, body=data.body, link="/classes/student",
        )

        teacher = self._db.get(User, teacher_id)
        return FeedItemSchema(
            id=activity.id, type="announcement",
            username=teacher.username if teacher else "?",
            payload=payload, created_at=activity.created_at,
        )

    def get_feed(self, class_id: int, user_id: int, limit: int = 30) -> List[FeedItemSchema]:
        self._get_class_or_404(class_id)
        self._require_membership(class_id, user_id)
        activities = self._group_dao.get_group_activities(class_id, limit=limit)
        # Noms d'utilisateurs en une requête.
        uids = {a.user_id for a in activities}
        names = dict(self._db.query(User.id, User.username).filter(User.id.in_(uids)).all()) if uids else {}
        return [
            FeedItemSchema(
                id=a.id, type=a.type, username=names.get(a.user_id, "?"),
                payload=a.payload, created_at=a.created_at,
            )
            for a in activities
        ]

    # ─── Classement & badges ────────────────────────────────────────────────────

    def _streaks(self, student_ids: List[int]) -> dict:
        """Streak (jours consécutifs d'étude) par élève — 1 requête."""
        if not student_ids:
            return {}
        rows = (
            self._db.query(StudySession.user_id, func.date(StudySession.created_at))
            .filter(StudySession.user_id.in_(student_ids))
            .distinct()
            .all()
        )
        by_user = {}
        for uid, d in rows:
            # func.date() -> str (SQLite) ou date (PG) : on normalise en date.
            if isinstance(d, str):
                d = date.fromisoformat(d)
            by_user.setdefault(uid, set()).add(d)

        today = datetime.utcnow().date()
        streaks = {}
        for uid in student_ids:
            days = by_user.get(uid, set())
            if today in days:
                cursor = today
            elif (today - timedelta(days=1)) in days:
                cursor = today - timedelta(days=1)
            else:
                streaks[uid] = 0
                continue
            count = 0
            while cursor in days:
                count += 1
                cursor -= timedelta(days=1)
            streaks[uid] = count
        return streaks

    @staticmethod
    def _badges(completed: int, avg_score: Optional[float], streak: int) -> List[str]:
        badges = []
        if completed >= 1:
            badges.append("Premier rendu")
        if completed >= 5:
            badges.append("Travailleur assidu")
        if streak >= 3:
            badges.append(f"Série de {streak} jours")
        if avg_score is not None and avg_score >= 80:
            badges.append("Excellence")
        return badges

    def get_leaderboard(self, class_id: int, user_id: int) -> LeaderboardSchema:
        group = self._get_class_or_404(class_id)
        self._require_membership(class_id, user_id)
        if not group.leaderboard_enabled:
            return LeaderboardSchema(enabled=False, entries=[])

        student_ids = self._student_ids(class_id)
        if not student_ids:
            return LeaderboardSchema(enabled=True, entries=[])

        # Devoirs complétés + score moyen par élève — 1 requête.
        rows = (
            self._db.query(
                AssignmentProgress.user_id,
                func.sum(case((AssignmentProgress.completed_at.isnot(None), 1), else_=0)),
                func.avg(AssignmentProgress.score_pct),
            )
            .join(Assignment, Assignment.id == AssignmentProgress.assignment_id)
            .filter(Assignment.group_id == class_id,
                    AssignmentProgress.user_id.in_(student_ids))
            .group_by(AssignmentProgress.user_id)
            .all()
        )
        stats = {r[0]: (int(r[1] or 0), float(r[2]) if r[2] is not None else None) for r in rows}

        streaks = self._streaks(student_ids)
        names = dict(self._db.query(User.id, User.username).filter(User.id.in_(student_ids)).all())

        entries = []
        for uid in student_ids:
            completed, avg = stats.get(uid, (0, None))
            streak = streaks.get(uid, 0)
            points = completed * 10 + streak * 5 + (int(avg / 10) if avg else 0)
            entries.append(LeaderboardEntrySchema(
                user_id=uid, username=names.get(uid, "?"),
                completed_assignments=completed, avg_score=avg, streak=streak,
                points=points, badges=self._badges(completed, avg, streak),
            ))
        entries.sort(key=lambda e: e.points, reverse=True)
        return LeaderboardSchema(enabled=True, entries=entries)

    # ─── Notifications ──────────────────────────────────────────────────────────

    def create_notifications_for_students(
        self, class_id: int, exclude_user_id: int, ntype: str,
        title: str, body: Optional[str] = None, link: Optional[str] = None,
    ) -> int:
        student_ids = [s for s in self._student_ids(class_id) if s != exclude_user_id]
        for sid in student_ids:
            self._db.add(Notification(
                user_id=sid, type=ntype, title=title, body=body,
                link=link, group_id=class_id,
            ))
        self._db.commit()
        return len(student_ids)

    def list_notifications(self, user_id: int, unread_only: bool = False, limit: int = 30) -> List[NotificationSchema]:
        q = self._db.query(Notification).filter(Notification.user_id == user_id)
        if unread_only:
            q = q.filter(Notification.read_at.is_(None))
        rows = q.order_by(Notification.created_at.desc(), Notification.id.desc()).limit(limit).all()
        return [
            NotificationSchema(
                id=n.id, type=n.type, title=n.title, body=n.body, link=n.link,
                read=n.read_at is not None, created_at=n.created_at,
            )
            for n in rows
        ]

    def unread_count(self, user_id: int) -> int:
        return (
            self._db.query(func.count(Notification.id))
            .filter(Notification.user_id == user_id, Notification.read_at.is_(None))
            .scalar()
        ) or 0

    def mark_read(self, user_id: int, notif_id: int) -> None:
        n = self._db.get(Notification, notif_id)
        if not n or n.user_id != user_id:
            raise ResourceNotFoundError("Notification introuvable.")
        if not n.read_at:
            n.read_at = datetime.utcnow()
            self._db.commit()

    def mark_all_read(self, user_id: int) -> int:
        count = (
            self._db.query(Notification)
            .filter(Notification.user_id == user_id, Notification.read_at.is_(None))
            .update({Notification.read_at: datetime.utcnow()}, synchronize_session=False)
        )
        self._db.commit()
        return count
