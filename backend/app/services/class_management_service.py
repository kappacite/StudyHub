"""
ClassManagementService — gestion de classe : trombinoscope (roster), code
d'invitation, et distribution de copies de cours aux élèves.

Le retrait de membre et le changement de rôle restent gérés par GroupService
(les classes sont des groupes) ; ce service couvre ce qui est propre aux classes.
"""
import string
import secrets
from typing import List

from sqlalchemy import func, case

from app.dao.group_dao import GroupDAO
from app.dao.binder_dao import BinderDAO
from app.models.group import Group, GroupMember, GroupBinder
from app.models.binder import Binder
from app.models.assignment import Assignment, AssignmentProgress
from app.models.study_session import StudySession
from app.models.notification import Notification
from app.models.user import User
from app.schemas.management_schema import (
    RosterEntrySchema, InviteCodeSchema, DistributeResultSchema, CourseBinderSchema,
)
from app.middlewares.error_handler import ResourceNotFoundError, ForbiddenError, ConflictError


class ClassManagementService:
    def __init__(self, group_dao: GroupDAO, binder_dao: BinderDAO):
        self._group_dao = group_dao
        self._binder_dao = binder_dao
        self._db = group_dao.db

    # ─── Helpers ──────────────────────────────────────────────────────────────

    def _get_class_or_404(self, class_id: int) -> Group:
        g = self._group_dao.get_by_id(class_id)
        if not g or not g.is_class:
            raise ResourceNotFoundError("Classe introuvable.")
        return g

    def _require_teacher(self, class_id: int, user_id: int) -> GroupMember:
        m = self._group_dao.get_group_member(class_id, user_id)
        if not m:
            raise ForbiddenError("Vous n'êtes pas membre de cette classe.")
        if m.role not in ("owner", "admin"):
            raise ForbiddenError("Action réservée au professeur.")
        return m

    def _generate_invite_code(self) -> str:
        alphabet = string.ascii_uppercase + string.digits
        for _ in range(50):
            code = ''.join(secrets.choice(alphabet) for _ in range(8))
            if not self._group_dao.get_by_invite_code(code):
                return code
        raise ConflictError("Impossible de générer un code d'invitation unique.")

    # ─── Roster ──────────────────────────────────────────────────────────────

    def get_roster(self, class_id: int, user_id: int) -> List[RosterEntrySchema]:
        self._get_class_or_404(class_id)
        self._require_teacher(class_id, user_id)

        members = (
            self._db.query(GroupMember.user_id, GroupMember.role,
                           GroupMember.joined_at, User.username)
            .join(User, User.id == GroupMember.user_id)
            .filter(GroupMember.group_id == class_id)
            .all()
        )
        member_ids = [m[0] for m in members]
        if not member_ids:
            return []

        # Devoirs complétés par membre (1 requête).
        completed = dict(
            self._db.query(
                AssignmentProgress.user_id,
                func.sum(case((AssignmentProgress.completed_at.isnot(None), 1), else_=0)),
            )
            .join(Assignment, Assignment.id == AssignmentProgress.assignment_id)
            .filter(Assignment.group_id == class_id,
                    AssignmentProgress.user_id.in_(member_ids))
            .group_by(AssignmentProgress.user_id)
            .all()
        )

        # Dernière activité (1 requête).
        last_active = dict(
            self._db.query(StudySession.user_id, func.max(StudySession.created_at))
            .filter(StudySession.user_id.in_(member_ids))
            .group_by(StudySession.user_id)
            .all()
        )

        roster = [
            RosterEntrySchema(
                user_id=uid, username=username, role=role, joined_at=joined_at,
                completed_assignments=int(completed.get(uid, 0) or 0),
                last_active=last_active.get(uid),
            )
            for (uid, role, joined_at, username) in members
        ]
        # Professeurs d'abord, puis par nom.
        roster.sort(key=lambda r: (r.role not in ("owner", "admin"), r.username.lower()))
        return roster

    # ─── Invitation ──────────────────────────────────────────────────────────

    def regenerate_invite(self, class_id: int, user_id: int) -> InviteCodeSchema:
        group = self._get_class_or_404(class_id)
        self._require_teacher(class_id, user_id)
        group.invite_code = self._generate_invite_code()
        self._db.commit()
        return InviteCodeSchema(invite_code=group.invite_code)

    # ─── Distribution de copies ──────────────────────────────────────────────

    def distribute_binder(self, class_id: int, user_id: int, binder_ref: str) -> DistributeResultSchema:
        """Clone un classeur dans le compte de chaque élève (copie personnelle)."""
        self._get_class_or_404(class_id)
        self._require_teacher(class_id, user_id)

        binder = self._binder_dao.get_by_id(binder_ref)
        if not binder or binder.user_id != user_id:
            raise ResourceNotFoundError("Classeur introuvable.")

        # Garantir que le classeur est partagé à la classe (prérequis du clone).
        if not self._group_dao.get_group_binder(class_id, binder._id):
            self._group_dao.add_group_binder(class_id, binder._id, "read", user_id)

        student_ids = [
            m.user_id for m in self._db.query(GroupMember).filter_by(group_id=class_id).all()
            if m.role not in ("owner", "admin")
        ]

        from app.services.community_service import CommunityService
        community = CommunityService()

        distributed = failed = 0
        for sid in student_ids:
            try:
                community.clone_package(sid, binder.id)
                self._db.add(Notification(
                    user_id=sid, type="course_shared", group_id=class_id,
                    title=f"Nouveau cours : {binder.name}",
                    body="Une copie a été ajoutée à vos classeurs.",
                    link="/binders",
                ))
                distributed += 1
            except Exception:
                self._db.rollback()
                failed += 1
        self._db.commit()
        return DistributeResultSchema(distributed=distributed, failed=failed)

    # ─── Dépôt de cours (B1) ─────────────────────────────────────────────────

    def get_or_create_course_binder(self, class_id: int, user_id: int) -> CourseBinderSchema:
        """Résout (ou crée) le classeur de cours de la classe : un classeur du prof
        partagé **par référence** à la classe. Les notes/PDF qu'il y dépose ensuite
        sont automatiquement visibles des élèves en lecture seule (cf. B2)."""
        cls = self._get_class_or_404(class_id)
        self._require_teacher(class_id, user_id)

        course_name = f"Cours — {cls.name}"

        # Réutiliser un classeur de cours déjà partagé à cette classe (idempotent).
        for gb in self._group_dao.get_group_binders(class_id):
            b = gb.binder
            if b and b.user_id == user_id and b.name == course_name:
                return CourseBinderSchema(binder_id=b.id, name=b.name, created=False)

        binder = Binder(user_id=user_id, name=course_name)
        self._db.add(binder)
        self._db.commit()
        self._group_dao.add_group_binder(class_id, binder._id, "read", user_id)
        return CourseBinderSchema(binder_id=binder.id, name=binder.name, created=True)
