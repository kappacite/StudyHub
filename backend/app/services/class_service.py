"""
ClassService — Logique métier pour les espaces de cours (type « class »).

Ce service compose avec GroupService : il gère la création d'une classe,
les devoirs (Assignment), et la progression individuelle des élèves.
"""
import string
import secrets
from datetime import datetime, timedelta
from typing import List, Optional

from app.dao.group_dao import GroupDAO
from app.dao.binder_dao import BinderDAO
from app.dao.user_dao import UserDAO
from app.dao.note_dao import NoteDAO
from app.dao.assignment_dao import AssignmentDAO
from app.dao.quiz_dao import QuizDAO
from app.dao.exam_dao import ExamDAO
from app.dao.evaluation_dao import EvaluationDAO
from app.dao.revision_dao import RevisionSetDAO
from app.extensions import db
from app.models.group import Group, GroupMember
from app.models.assignment import (
    Assignment, AssignmentTask, AssignmentTaskProgress, AssignmentProgress,
)
from app.models.binder import Binder
from app.models.user import User
from app.schemas.class_schema import (
    ClassCreateSchema, AssignmentCreateSchema,
    AssignmentResponseSchema, AssignmentSummarySchema,
    AssignmentProgressResponseSchema, ClassResponseSchema,
    BinderProgressResponseSchema, StudentMaterialsProgressResponseSchema,
    AssignmentTaskResponseSchema,
)
from app.middlewares.error_handler import (
    ResourceNotFoundError, ForbiddenError, ConflictError, ValidationError
)


# Pour chaque type de tâche, la nature de la cible (et le DAO qui la résout).
TASK_TARGET_KIND = {
    "flashcards": "binder",
    "exam": "binder",
    "quiz": "note",
    "blurting": "note",
    "read": "note",
    "revision": "revision_set",
}


class ClassService:
    def __init__(
        self,
        group_dao: GroupDAO,
        binder_dao: BinderDAO,
        user_dao: UserDAO,
        note_dao: NoteDAO = None,
        assignment_dao: AssignmentDAO = None,
        quiz_dao: QuizDAO = None,
        exam_dao: ExamDAO = None,
        evaluation_dao: EvaluationDAO = None,
    ):
        self._group_dao = group_dao
        self._binder_dao = binder_dao
        self._user_dao = user_dao
        # DAOs additionnels : créés à la volée depuis la session si non injectés,
        # pour ne pas casser les appelants existants (focus_service, etc.).
        session = group_dao.db
        self._note_dao = note_dao or NoteDAO(session)
        self._assignment_dao = assignment_dao or AssignmentDAO(session)
        self._quiz_dao = quiz_dao or QuizDAO(session)
        self._exam_dao = exam_dao or ExamDAO(session)
        self._evaluation_dao = evaluation_dao or EvaluationDAO(session)
        self._revision_set_dao = RevisionSetDAO(session)

    # ─────────────────────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _generate_invite_code(self) -> str:
        alphabet = string.ascii_uppercase + string.digits
        for _ in range(50):
            code = ''.join(secrets.choice(alphabet) for _ in range(8))
            if not self._group_dao.get_by_invite_code(code):
                return code
        raise ConflictError("Impossible de générer un code d'invitation unique.")

    def _require_membership(self, group_id: int, user_id: int) -> GroupMember:
        member = self._group_dao.get_group_member(group_id, user_id)
        if not member:
            raise ForbiddenError("Vous n'êtes pas membre de cette classe.")
        return member

    def _require_teacher(self, group_id: int, user_id: int) -> GroupMember:
        """Exige le rôle owner ou admin (= professeur)."""
        member = self._require_membership(group_id, user_id)
        if member.role not in ("owner", "admin"):
            raise ForbiddenError("Cette action est réservée aux professeurs (owner/admin).")
        return member

    def _get_class_or_404(self, class_id: int) -> Group:
        group = self._group_dao.get_by_id(class_id)
        if not group or not group.is_class:
            raise ResourceNotFoundError("Classe introuvable.")
        return group

    def _get_assignment_or_404(self, class_id: int, assignment_id: int) -> Assignment:
        asgn = db.session.get(Assignment, assignment_id)
        if not asgn or asgn.group_id != class_id:
            raise ResourceNotFoundError("Devoir introuvable.")
        return asgn

    def _binder_name(self, binder_id: int) -> str:
        b = db.session.get(Binder, binder_id)
        return b.name if b else f"Classeur #{binder_id}"

    def _group_name(self, group_id: int) -> str:
        g = self._group_dao.get_by_id(group_id)
        return g.name if g else f"Classe #{group_id}"

    def _serialize_task(self, task: AssignmentTask, viewer_id: int = None) -> AssignmentTaskResponseSchema:
        my_status = my_score = my_completed = None
        if viewer_id is not None:
            prog = self._assignment_dao.get_task_progress(task.id, viewer_id)
            if prog:
                my_status, my_score, my_completed = prog.status, prog.score_pct, prog.completed_at
        return AssignmentTaskResponseSchema(
            id=task.id,
            task_type=task.task_type,
            ref_id=task.ref_id,
            ref_uuid=task.ref_uuid,
            ref_label=task.ref_label,
            goal=task.goal,
            order=task.order,
            my_status=my_status,
            my_score_pct=my_score,
            my_completed_at=my_completed,
        )

    def _display_binder(self, asgn: Assignment):
        """Classeur « principal » d'un devoir (rétro-compat : binder_id en réponse)."""
        if asgn.binder:
            return asgn.binder.id, asgn.binder.name
        for t in asgn.tasks:
            if t.task_type in ("flashcards", "exam") and t.ref_uuid:
                return t.ref_uuid, t.ref_label or ""
        return "", ""

    def _serialize_assignment(
        self, asgn: Assignment, include_progress: bool = True, viewer_id: int = None
    ) -> AssignmentResponseSchema:
        progress_list = []
        if include_progress:
            for p in asgn.progresses:
                user = db.session.get(User, p.user_id)
                progress_list.append(AssignmentProgressResponseSchema(
                    user_id=p.user_id,
                    username=user.username if user else "?",
                    cards_reviewed=p.cards_reviewed,
                    score_pct=p.score_pct,
                    completed_at=p.completed_at,
                    teacher_score=p.teacher_score,
                    teacher_feedback=p.teacher_feedback,
                    graded_at=p.graded_at,
                ))

        binder_uuid, binder_name = self._display_binder(asgn)
        return AssignmentResponseSchema(
            id=asgn.id,
            group_id=asgn.group_id,
            binder_id=binder_uuid,
            binder_name=binder_name,
            title=asgn.title,
            description=asgn.description,
            instructions=asgn.instructions,
            due_date=asgn.due_date,
            publish_at=asgn.publish_at,
            allow_late=asgn.allow_late,
            created_by=asgn.created_by,
            created_at=asgn.created_at,
            tasks=[self._serialize_task(t, viewer_id) for t in asgn.tasks],
            progress=progress_list
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Résolution des cibles de tâches & recalcul de progression
    # ─────────────────────────────────────────────────────────────────────────

    def _resolve_task_target(self, owner_id: int, task_type: str, ref: str):
        """Résout la cible d'une tâche → (ref_id interne, ref_uuid public, ref_label)."""
        kind = TASK_TARGET_KIND.get(task_type)
        if kind is None:
            raise ValidationError(f"Type de tâche inconnu : {task_type}")
        if kind == "binder":
            binder = self._binder_dao.get_by_id(ref)
            if not binder or binder.user_id != owner_id:
                raise ResourceNotFoundError("Classeur introuvable pour cette tâche.")
            return binder._id, binder.id, binder.name
        if kind == "revision_set":
            try:
                set_id = int(ref)
            except (TypeError, ValueError):
                raise ValidationError("Identifiant d'ensemble de révision invalide.")
            rset = self._revision_set_dao.get_by_id(set_id)
            if not rset or rset.user_id != owner_id:
                raise ResourceNotFoundError("Ensemble de révision introuvable pour cette tâche.")
            return rset.id, None, rset.name
        note = self._note_dao.get_by_id(ref)
        if not note or note.user_id != owner_id:
            raise ResourceNotFoundError("Note introuvable pour cette tâche.")
        return note._id, note.id, note.title

    # ─────────────────────────────────────────────────────────────────────────
    # Création de classe
    # ─────────────────────────────────────────────────────────────────────────

    def get_my_classes(self, user_id: int) -> List[ClassResponseSchema]:
        groups = self._group_dao.get_user_groups(user_id)
        response = []
        for g in groups:
            if not g.is_class:
                continue
            members_count = len(g.members_assoc)
            my_role = next(
                (m.role for m in g.members_assoc if m.user_id == user_id), None
            )
            response.append(
                ClassResponseSchema(
                    id=g.id,
                    name=g.name,
                    description=g.description,
                    invite_code=g.invite_code,
                    type=g.type,
                    is_class=g.is_class,
                    is_public=g.is_public,
                    created_by=g.created_by,
                    created_at=g.created_at,
                    members_count=members_count,
                    my_role=my_role,
                )
            )
        return response

    def create_class(self, user_id: int, data: ClassCreateSchema) -> ClassResponseSchema:
        # Limite : max 5 groupes/classes créés
        created_count = self._group_dao.count_user_created_groups(user_id)
        if created_count >= 5:
            raise ForbiddenError("Vous ne pouvez pas créer plus de 5 groupes/classes.")

        joined_count = self._group_dao.count_user_joined_groups(user_id)
        if joined_count >= 20:
            raise ForbiddenError("Vous ne pouvez pas appartenir à plus de 20 groupes/classes.")

        invite_code = self._generate_invite_code()
        group = Group(
            name=data.name,
            description=data.description,
            invite_code=invite_code,
            created_by=user_id,
            type="class",
            is_class=True,
            is_public=data.is_public or False
        )
        created = self._group_dao.create(group)
        self._group_dao.add_group_member(created.id, user_id, "owner")

        members_count = db.session.query(GroupMember).filter_by(group_id=created.id).count()
        return ClassResponseSchema(
            id=created.id,
            name=created.name,
            description=created.description,
            invite_code=created.invite_code,
            type=created.type,
            is_class=created.is_class,
            is_public=created.is_public,
            created_by=created.created_by,
            created_at=created.created_at,
            members_count=members_count
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Devoirs
    # ─────────────────────────────────────────────────────────────────────────

    def create_assignment(
        self, class_id: int, user_id: int, data: AssignmentCreateSchema
    ) -> AssignmentResponseSchema:
        self._get_class_or_404(class_id)
        self._require_teacher(class_id, user_id)

        # Déterminer la liste des tâches : voie multi-tâches ou voie legacy mono-classeur.
        if data.tasks:
            task_specs = [(t.task_type, t.ref, t.goal) for t in data.tasks]
        else:
            task_specs = [("flashcards", data.binder_id, None)]

        resolved = []  # (task_type, ref_id, ref_uuid, ref_label, goal)
        for task_type, ref, goal in task_specs:
            ref_id, ref_uuid, ref_label = self._resolve_task_target(user_id, task_type, ref)
            resolved.append((task_type, ref_id, ref_uuid, ref_label, goal))

        # binder_id « principal » pour la rétro-compat de l'affichage.
        legacy_binder_id = next(
            (r[1] for r in resolved if r[0] in ("flashcards", "exam")), None
        )

        asgn = Assignment(
            group_id=class_id,
            binder_id=legacy_binder_id,
            title=data.title,
            description=data.description,
            instructions=data.instructions,
            due_date=data.due_date,
            publish_at=data.publish_at,
            allow_late=data.allow_late,
            created_by=user_id,
        )
        db.session.add(asgn)
        db.session.flush()

        for order, (task_type, ref_id, ref_uuid, ref_label, goal) in enumerate(resolved):
            db.session.add(AssignmentTask(
                assignment_id=asgn.id, task_type=task_type, ref_id=ref_id,
                ref_uuid=ref_uuid, ref_label=ref_label, goal=goal, order=order,
            ))
        db.session.flush()

        # Initialiser l'agrégat + la progression par tâche pour chaque élève.
        members = db.session.query(GroupMember).filter_by(group_id=class_id).all()
        student_ids = [m.user_id for m in members if m.user_id != user_id]
        from app.models.notification import Notification
        for sid in student_ids:
            db.session.add(AssignmentProgress(assignment_id=asgn.id, user_id=sid))
            for task in asgn.tasks:
                db.session.add(AssignmentTaskProgress(task_id=task.id, user_id=sid))
            # Notifier l'élève du nouveau devoir.
            db.session.add(Notification(
                user_id=sid, type="new_assignment", group_id=class_id,
                title=f"Nouveau devoir : {asgn.title}",
                body=asgn.description, link="/classes/student",
            ))
        db.session.commit()
        db.session.refresh(asgn)

        return self._serialize_assignment(asgn)

    def list_assignments(self, class_id: int, user_id: int) -> List[AssignmentResponseSchema]:
        self._get_class_or_404(class_id)
        self._require_membership(class_id, user_id)
        asgns = db.session.query(Assignment).filter_by(group_id=class_id).order_by(Assignment.due_date).all()
        return [self._serialize_assignment(a, include_progress=False, viewer_id=user_id) for a in asgns]

    def get_assignment(self, class_id: int, assignment_id: int, user_id: int) -> AssignmentResponseSchema:
        self._get_class_or_404(class_id)
        self._require_teacher(class_id, user_id)  # seul le prof voit la progression de tous
        asgn = self._get_assignment_or_404(class_id, assignment_id)
        return self._serialize_assignment(asgn, include_progress=True)

    def delete_assignment(self, class_id: int, assignment_id: int, user_id: int) -> None:
        self._get_class_or_404(class_id)
        self._require_teacher(class_id, user_id)
        asgn = self._get_assignment_or_404(class_id, assignment_id)
        db.session.delete(asgn)
        db.session.commit()

    def grade_submission(
        self, class_id: int, assignment_id: int, student_id: int, teacher_id: int, data
    ) -> AssignmentProgressResponseSchema:
        """Le professeur note/commente la soumission d'un élève."""
        self._get_class_or_404(class_id)
        self._require_teacher(class_id, teacher_id)
        asgn = self._get_assignment_or_404(class_id, assignment_id)

        if not self._group_dao.get_group_member(class_id, student_id):
            raise ResourceNotFoundError("Cet élève n'est pas membre de la classe.")

        sub = self._assignment_dao.upsert_submission(asgn.id, student_id, commit=False)
        if data.teacher_score is not None:
            sub.teacher_score = data.teacher_score
        if data.teacher_feedback is not None:
            sub.teacher_feedback = data.teacher_feedback
        sub.graded_by = teacher_id
        sub.graded_at = datetime.utcnow()
        db.session.commit()

        student = db.session.get(User, student_id)
        return AssignmentProgressResponseSchema(
            user_id=student_id,
            username=student.username if student else "?",
            cards_reviewed=sub.cards_reviewed,
            score_pct=sub.score_pct,
            completed_at=sub.completed_at,
            teacher_score=sub.teacher_score,
            teacher_feedback=sub.teacher_feedback,
            graded_at=sub.graded_at,
        )

    def submit_task(
        self, class_id: int, assignment_id: int, task_id: int, user_id: int, data=None
    ) -> AssignmentTaskResponseSchema:
        """Un élève soumet/valide une tâche. Recalcule la progression depuis l'état
        du module sous-jacent (quiz/exam/blurting/flashcards) ; pour les tâches de
        lecture, marque simplement la tâche comme faite."""
        self._get_class_or_404(class_id)
        self._require_membership(class_id, user_id)

        asgn = self._get_assignment_or_404(class_id, assignment_id)
        task = self._assignment_dao.get_task(task_id)
        if not task or task.assignment_id != asgn.id:
            raise ResourceNotFoundError("Tâche introuvable.")

        recompute_task_for_user(db.session, user_id, task, mark_read_done=True)
        recompute_assignment_for_user(db.session, user_id, asgn)
        db.session.commit()

        return self._serialize_task(task, viewer_id=user_id)

    # ─────────────────────────────────────────────────────────────────────────
    # Progression des élèves
    # ─────────────────────────────────────────────────────────────────────────

    def get_student_progress(
        self, class_id: int, student_id: int, requester_id: int
    ) -> List[AssignmentProgressResponseSchema]:
        """Progression individuelle d'un élève — réservé au professeur."""
        self._get_class_or_404(class_id)
        self._require_teacher(class_id, requester_id)

        # Vérifier que student_id est membre
        student_member = self._group_dao.get_group_member(class_id, student_id)
        if not student_member:
            raise ResourceNotFoundError("Cet élève n'est pas membre de la classe.")

        student = db.session.get(User, student_id)
        asgns = db.session.query(Assignment).filter_by(group_id=class_id).all()
        result = []
        for asgn in asgns:
            prog = db.session.get(AssignmentProgress, (asgn.id, student_id))
            result.append(AssignmentProgressResponseSchema(
                user_id=student_id,
                username=student.username if student else "?",
                cards_reviewed=prog.cards_reviewed if prog else 0,
                score_pct=prog.score_pct if prog else None,
                completed_at=prog.completed_at if prog else None
            ))
        return result

    # ─────────────────────────────────────────────────────────────────────────
    # Vue élève — devoirs assignés à moi
    # ─────────────────────────────────────────────────────────────────────────

    def get_my_assignments(self, user_id: int) -> List[AssignmentSummarySchema]:
        """Tous les devoirs assignés à cet utilisateur dans toutes ses classes."""
        now = datetime.utcnow()

        # Trouver les classes dont l'utilisateur est membre (pas owner)
        memberships = (
            db.session.query(GroupMember)
            .join(Group, GroupMember.group_id == Group.id)
            .filter(
                GroupMember.user_id == user_id,
                Group.is_class == True
            )
            .all()
        )

        result = []
        dirty = False
        for membership in memberships:
            group = self._group_dao.get_by_id(membership.group_id)
            asgns = db.session.query(Assignment).filter_by(group_id=membership.group_id).all()
            for asgn in asgns:
                # Recalcul à la lecture : le statut « fait » doit refléter l'état réel des
                # modules (QCM/examen/blurting/flashcards/révision), sans dépendre d'une
                # validation manuelle ni d'un hook par module. recompute_* ne commit pas ;
                # on persiste en une fois après la boucle.
                prog = recompute_assignment_for_user(db.session, user_id, asgn)
                dirty = True

                # Calcul du statut
                if prog and prog.completed_at:
                    status = "done"
                elif asgn.due_date and now > asgn.due_date:
                    status = "late"
                elif prog and prog.cards_reviewed > 0:
                    status = "in_progress"
                else:
                    status = "todo"

                binder_uuid, binder_name = self._display_binder(asgn)
                result.append(AssignmentSummarySchema(
                    id=asgn.id,
                    group_id=asgn.group_id,
                    group_name=group.name if group else "",
                    binder_id=binder_uuid,
                    binder_name=binder_name,
                    title=asgn.title,
                    description=asgn.description,
                    due_date=asgn.due_date,
                    created_at=asgn.created_at,
                    my_cards_reviewed=prog.cards_reviewed if prog else 0,
                    my_score_pct=prog.score_pct if prog else None,
                    my_completed_at=prog.completed_at if prog else None,
                    status=status,
                    tasks=[self._serialize_task(t, viewer_id=user_id) for t in asgn.tasks],
                ))

        if dirty:
            db.session.commit()

        # Trier : late et todo d'abord, puis par deadline
        def sort_key(a: AssignmentSummarySchema):
            priority = {"late": 0, "todo": 1, "in_progress": 2, "done": 3}
            return (priority.get(a.status, 99), a.due_date or datetime(9999, 12, 31))

        result.sort(key=sort_key)
        return result

    def get_assignments_due_soon(self, user_id: int, days: int = 3) -> List[AssignmentSummarySchema]:
        """Devoirs avec deadline dans les prochains `days` jours — pour le Focus."""
        now = datetime.utcnow()
        deadline = now + timedelta(days=days)
        all_asgns = self.get_my_assignments(user_id)
        return [
            a for a in all_asgns
            if a.due_date and now <= a.due_date <= deadline and a.status != "done"
        ]

    def list_public_classes(self, search: Optional[str] = None) -> List[ClassResponseSchema]:
        query = db.session.query(Group).filter(Group.is_class == True, Group.is_public == True)
        if search:
            query = query.filter(Group.name.ilike(f"%{search}%") | Group.description.ilike(f"%{search}%"))
        classes = query.order_by(Group.created_at.desc()).all()
        
        response = []
        for g in classes:
            members_count = len(g.members_assoc)
            response.append(
                ClassResponseSchema(
                    id=g.id,
                    name=g.name,
                    description=g.description,
                    invite_code=g.invite_code,
                    type=g.type,
                    is_class=g.is_class,
                    is_public=g.is_public,
                    created_by=g.created_by,
                    created_at=g.created_at,
                    members_count=members_count
                )
            )
        return response

    def follow_class(self, user_id: int, class_id: int) -> ClassResponseSchema:
        from app.middlewares.error_handler import ConflictError
        cls = self._get_class_or_404(class_id)
        if not cls.is_public:
            raise ForbiddenError("Vous ne pouvez pas suivre une classe privée.")
            
        existing = self._group_dao.get_group_member(class_id, user_id)
        if existing:
            raise ConflictError("Vous suivez déjà cette classe ou en êtes membre.")
            
        self._group_dao.add_group_member(class_id, user_id, "follower")
        db.session.commit()
        
        members_count = len(cls.members_assoc)
        return ClassResponseSchema(
            id=cls.id,
            name=cls.name,
            description=cls.description,
            invite_code=cls.invite_code,
            type=cls.type,
            is_class=cls.is_class,
            is_public=cls.is_public,
            created_by=cls.created_by,
            created_at=cls.created_at,
            members_count=members_count
        )

    def get_class_materials_progress(
        self, class_id: int, user_id: int
    ) -> List[StudentMaterialsProgressResponseSchema]:
        self._get_class_or_404(class_id)
        self._require_teacher(class_id, user_id)

        group = self._group_dao.get_by_id(class_id)
        students = []
        for m in group.members_assoc:
            if m.role not in ("owner", "admin"):
                students.append(m.user)

        shared_binders = [assoc.binder for assoc in group.binders_assoc if assoc.binder]

        results = []
        from app.models.study_session import StudySession
        from sqlalchemy import func

        for student in students:
            binders_progress = []
            for binder in shared_binders:
                card_ids = get_all_card_ids_in_binder(db.session, binder._id)
                total_cards = len(card_ids)

                if total_cards == 0:
                    binders_progress.append(
                        BinderProgressResponseSchema(
                            binder_id=binder.id,
                            binder_name=binder.name,
                            cards_reviewed=0,
                            total_cards=0,
                            score_pct=100.0,
                            last_reviewed_at=None
                        )
                    )
                    continue

                sessions = (
                    db.session.query(
                        StudySession.flashcard_id,
                        func.sum(StudySession.cards_reviewed).label("reviewed"),
                        func.sum(StudySession.cards_correct).label("correct"),
                        func.max(StudySession.created_at).label("last_reviewed")
                    )
                    .filter(
                        StudySession.user_id == student.id,
                        StudySession.module == "flashcard",
                        StudySession.flashcard_id.in_(card_ids)
                    )
                    .group_by(StudySession.flashcard_id)
                    .all()
                )

                reviewed_card_ids = {s[0] for s in sessions if s[0]}
                unique_reviewed = len(reviewed_card_ids)

                total_reviewed = sum(s[1] or 0 for s in sessions)
                total_correct = sum(s[2] or 0 for s in sessions)
                score_pct = (total_correct / total_reviewed * 100.0) if total_reviewed > 0 else 0.0
                last_reviewed_at = max(s[3] for s in sessions if s[3]) if sessions else None

                binders_progress.append(
                    BinderProgressResponseSchema(
                        binder_id=binder.id,
                        binder_name=binder.name,
                        cards_reviewed=unique_reviewed,
                        total_cards=total_cards,
                        score_pct=score_pct,
                        last_reviewed_at=last_reviewed_at
                    )
                )

            results.append(
                StudentMaterialsProgressResponseSchema(
                    user_id=student.id,
                    username=student.username,
                    binders_progress=binders_progress
                )
            )

        return results


def get_all_card_ids_in_binder(db_session, binder_id: int) -> List[int]:
    card_ids = []
    
    from app.models.deck import Deck
    from app.models.flashcard import Flashcard
    from app.models.binder import Binder
    
    def collect_cards(b_id):
        decks = db_session.query(Deck).filter_by(binder_id=b_id).all()
        for d in decks:
            cards = db_session.query(Flashcard.id).filter_by(deck_id=d.id).all()
            card_ids.extend([c[0] for c in cards])
            
        children = db_session.query(Binder._id).filter_by(parent_id=b_id).all()
        for child_id_tup in children:
            collect_cards(child_id_tup[0])
            
    collect_cards(binder_id)
    return card_ids


def _flashcards_state(db_session, user_id, binder_id, created_after, goal):
    """Calcule l'état d'une tâche flashcards : (status, score, completed_at, payload)."""
    from app.models.study_session import StudySession

    card_ids = get_all_card_ids_in_binder(db_session, binder_id) if binder_id else []
    total_cards = len(card_ids)
    payload = {"cards_reviewed": 0, "total_cards": total_cards}

    if total_cards == 0:
        # Classeur vide (rien à réviser / mal configuré) : la tâche n'est PAS « faite ».
        # Cohérent avec les ensembles de révision vides (cf. _revision_state, #4) —
        # sinon un devoir flashcards sur classeur vide se marquerait « fait » au simple
        # affichage (recalcul à la lecture de get_my_assignments).
        return "todo", None, None, payload

    sessions = (
        db_session.query(StudySession)
        .filter(
            StudySession.user_id == user_id,
            StudySession.module == "flashcard",
            StudySession.flashcard_id.in_(card_ids),
            StudySession.created_at >= created_after - timedelta(seconds=5),
        )
        .all()
    )
    unique_reviewed = len({s.flashcard_id for s in sessions if s.flashcard_id})
    total_reviewed = sum(s.cards_reviewed or 0 for s in sessions)
    total_correct = sum(s.cards_correct or 0 for s in sessions)
    score_pct = (total_correct / total_reviewed * 100.0) if total_reviewed > 0 else 0.0
    payload["cards_reviewed"] = unique_reviewed

    goal = goal or {}
    threshold = total_cards
    if goal.get("min_cards"):
        threshold = min(int(goal["min_cards"]), total_cards)
    cards_ok = unique_reviewed >= threshold and threshold > 0
    score_ok = (score_pct >= goal["min_score"]) if goal.get("min_score") else True
    done = cards_ok and score_ok

    if done:
        return "done", score_pct, datetime.utcnow(), payload
    status = "in_progress" if unique_reviewed > 0 else "todo"
    return status, (score_pct if unique_reviewed > 0 else None), None, payload


def _revision_state(db_session, user_id, set_id, created_after, goal):
    """État d'une tâche `revision` : dérivé des `StudySession` des items de l'ensemble."""
    from app.models.study_session import StudySession
    from app.models.revision import RevisionSet, RevisionItem

    rset = db_session.get(RevisionSet, set_id) if set_id else None
    if not rset:
        return "todo", None, None, {"reviewed": 0, "total": 0}

    item_ids = [r.id for r in db_session.query(RevisionItem.id).filter(RevisionItem.set_id == set_id).all()]
    total = len(item_ids)
    payload = {"reviewed": 0, "total": total}
    if total == 0:
        # Un ensemble sans item n'est pas « fait » : rien à réviser ⇒ à faire.
        return "todo", None, None, payload

    sessions = (
        db_session.query(StudySession)
        .filter(
            StudySession.user_id == user_id,
            StudySession.item_type == rset.type,
            StudySession.item_id.in_(item_ids),
            StudySession.created_at >= created_after - timedelta(seconds=5),
        )
        .all()
    )
    graded = [s for s in sessions if s.grade is not None]
    unique_reviewed = len({s.item_id for s in sessions if s.item_id})
    successes = sum(1 for s in graded if s.grade >= 3)
    score_pct = (successes / len(graded) * 100.0) if graded else 0.0
    payload["reviewed"] = unique_reviewed

    goal = goal or {}
    threshold = total
    if goal.get("min_items"):
        threshold = min(int(goal["min_items"]), total)
    items_ok = unique_reviewed >= threshold and threshold > 0
    score_ok = (score_pct >= goal["min_score"]) if goal.get("min_score") else True
    done = items_ok and score_ok

    if done:
        return "done", score_pct, datetime.utcnow(), payload
    status = "in_progress" if unique_reviewed > 0 else "todo"
    return status, (score_pct if unique_reviewed > 0 else None), None, payload


def _module_completion_state(db_session, user_id, task):
    """État d'une tâche quiz/exam/blurting depuis le module sous-jacent."""
    if task.task_type == "exam":
        from app.models.exam import ExamSession
        row = (
            db_session.query(ExamSession)
            .filter(ExamSession.binder_id == task.ref_id,
                    ExamSession.user_id == user_id,
                    ExamSession.completed_at.isnot(None))
            .order_by(ExamSession.score_pct.desc().nullslast())
            .first()
        )
    elif task.task_type == "quiz":
        from app.models.quiz import Quiz
        row = (
            db_session.query(Quiz)
            .filter(Quiz.note_id == task.ref_id,
                    Quiz.user_id == user_id,
                    Quiz.completed_at.isnot(None))
            .order_by(Quiz.score_pct.desc().nullslast())
            .first()
        )
    else:  # blurting
        from app.models.evaluation import Evaluation
        row = (
            db_session.query(Evaluation)
            .filter(Evaluation.note_id == task.ref_id,
                    Evaluation.user_id == user_id,
                    Evaluation.completed_at.isnot(None))
            .order_by(Evaluation.score_pct.desc().nullslast())
            .first()
        )
    if not row:
        return "todo", None, None, None
    return "done", row.score_pct, row.completed_at, None


def recompute_task_for_user(db_session, user_id, task, mark_read_done=False):
    """Recalcule la progression d'un élève sur une tâche et la persiste (sans commit)."""
    prog = db_session.get(AssignmentTaskProgress, (task.id, user_id))
    if not prog:
        prog = AssignmentTaskProgress(task_id=task.id, user_id=user_id)
        db_session.add(prog)

    if task.task_type in ("flashcards",):
        created_after = task.assignment.created_at if task.assignment else datetime.utcnow()
        status, score, completed, payload = _flashcards_state(
            db_session, user_id, task.ref_id, created_after, task.goal
        )
    elif task.task_type == "revision":
        created_after = task.assignment.created_at if task.assignment else datetime.utcnow()
        status, score, completed, payload = _revision_state(
            db_session, user_id, task.ref_id, created_after, task.goal
        )
    elif task.task_type in ("exam", "quiz", "blurting"):
        status, score, completed, payload = _module_completion_state(db_session, user_id, task)
    elif task.task_type == "read":
        # Lecture : complétion manuelle uniquement.
        if mark_read_done:
            status, score, completed, payload = "done", None, datetime.utcnow(), None
        else:
            return prog  # on ne dégrade pas une lecture déjà validée
    else:
        return prog

    prog.status = status
    prog.score_pct = score
    if completed and not prog.completed_at:
        prog.completed_at = completed
    elif not completed:
        prog.completed_at = None
    if status != "todo" and not prog.submitted_at:
        prog.submitted_at = datetime.utcnow()
    prog.payload = payload
    return prog


def recompute_assignment_for_user(db_session, user_id, assignment):
    """Recalcule toutes les tâches d'un devoir pour un élève + l'agrégat (soumission)."""
    task_progs = []
    cards_reviewed = 0
    scores = []
    for task in assignment.tasks:
        prog = recompute_task_for_user(db_session, user_id, task)
        task_progs.append(prog)
        if task.task_type == "flashcards" and prog.payload:
            cards_reviewed += prog.payload.get("cards_reviewed", 0)
        if prog.score_pct is not None:
            scores.append(prog.score_pct)

    sub = db_session.get(AssignmentProgress, (assignment.id, user_id))
    if not sub:
        sub = AssignmentProgress(assignment_id=assignment.id, user_id=user_id)
        db_session.add(sub)
    sub.cards_reviewed = cards_reviewed
    sub.score_pct = (sum(scores) / len(scores)) if scores else None
    all_done = bool(task_progs) and all(p.status == "done" for p in task_progs)
    if all_done and not sub.completed_at:
        sub.completed_at = datetime.utcnow()
    elif not all_done:
        sub.completed_at = None
    return sub


# Rétro-compatibilité : ancienne API appelée depuis le flux flashcards.
def update_assignment_progress(db_session, user_id: int, assignment_id: int):
    assignment = db_session.get(Assignment, assignment_id)
    if not assignment:
        return
    recompute_assignment_for_user(db_session, user_id, assignment)
    db_session.commit()


def trigger_assignment_progress_update(db_session, user_id: int, card_id: int):
    """Quand un élève répond à une carte, recalcule les devoirs (tâches flashcards/exam)
    dont la cible (classeur) contient cette carte."""
    from app.models.flashcard import Flashcard
    from app.models.deck import Deck
    from app.models.binder import Binder

    card = db_session.get(Flashcard, card_id)
    if not card or not card.deck_id:
        return
    deck = db_session.get(Deck, card.deck_id)
    if not deck or not deck.binder_id:
        return

    binder_ids = []
    curr_binder_id = deck.binder_id
    while curr_binder_id:
        binder_ids.append(curr_binder_id)
        b = db_session.get(Binder, curr_binder_id)
        curr_binder_id = b.parent_id if b else None
    if not binder_ids:
        return

    from app.models.group import GroupMember

    # Devoirs de l'élève dont une tâche flashcards/exam cible un de ces classeurs.
    assignments = (
        db_session.query(Assignment)
        .join(GroupMember, Assignment.group_id == GroupMember.group_id)
        .join(AssignmentTask, AssignmentTask.assignment_id == Assignment.id)
        .filter(
            GroupMember.user_id == user_id,
            AssignmentTask.task_type.in_(("flashcards", "exam")),
            AssignmentTask.ref_id.in_(binder_ids),
        )
        .distinct()
        .all()
    )
    for asgn in assignments:
        recompute_assignment_for_user(db_session, user_id, asgn)
    if assignments:
        db_session.commit()
