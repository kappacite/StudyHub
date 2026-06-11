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
from app.extensions import db
from app.models.group import Group, GroupMember
from app.models.assignment import Assignment, AssignmentProgress
from app.models.binder import Binder
from app.models.user import User
from app.schemas.class_schema import (
    ClassCreateSchema, AssignmentCreateSchema,
    AssignmentResponseSchema, AssignmentSummarySchema,
    AssignmentProgressResponseSchema, ClassResponseSchema,
    BinderProgressResponseSchema, StudentMaterialsProgressResponseSchema
)
from app.middlewares.error_handler import (
    ResourceNotFoundError, ForbiddenError, ConflictError
)


class ClassService:
    def __init__(self, group_dao: GroupDAO, binder_dao: BinderDAO, user_dao: UserDAO):
        self._group_dao = group_dao
        self._binder_dao = binder_dao
        self._user_dao = user_dao

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

    def _serialize_assignment(self, asgn: Assignment, include_progress: bool = True) -> AssignmentResponseSchema:
        progress_list = []
        if include_progress:
            for p in asgn.progresses:
                user = db.session.get(User, p.user_id)
                progress_list.append(AssignmentProgressResponseSchema(
                    user_id=p.user_id,
                    username=user.username if user else "?",
                    cards_reviewed=p.cards_reviewed,
                    score_pct=p.score_pct,
                    completed_at=p.completed_at
                ))

        return AssignmentResponseSchema(
            id=asgn.id,
            group_id=asgn.group_id,
            binder_id=asgn.binder_id,
            binder_name=self._binder_name(asgn.binder_id),
            title=asgn.title,
            description=asgn.description,
            due_date=asgn.due_date,
            created_by=asgn.created_by,
            created_at=asgn.created_at,
            progress=progress_list
        )

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

        binder = db.session.get(Binder, data.binder_id)
        if not binder:
            raise ResourceNotFoundError("Classeur introuvable.")

        asgn = Assignment(
            group_id=class_id,
            binder_id=data.binder_id,
            title=data.title,
            description=data.description,
            due_date=data.due_date,
            created_by=user_id
        )
        db.session.add(asgn)
        db.session.commit()
        db.session.refresh(asgn)

        # Initialiser le progress pour tous les membres élèves
        members = db.session.query(GroupMember).filter_by(group_id=class_id).all()
        for m in members:
            if m.user_id != user_id:  # pas le prof
                prog = AssignmentProgress(assignment_id=asgn.id, user_id=m.user_id)
                db.session.add(prog)
        db.session.commit()

        return self._serialize_assignment(asgn)

    def list_assignments(self, class_id: int, user_id: int) -> List[AssignmentResponseSchema]:
        self._get_class_or_404(class_id)
        self._require_membership(class_id, user_id)
        asgns = db.session.query(Assignment).filter_by(group_id=class_id).order_by(Assignment.due_date).all()
        return [self._serialize_assignment(a, include_progress=False) for a in asgns]

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
        for membership in memberships:
            group = self._group_dao.get_by_id(membership.group_id)
            asgns = db.session.query(Assignment).filter_by(group_id=membership.group_id).all()
            for asgn in asgns:
                prog = db.session.get(AssignmentProgress, (asgn.id, user_id))

                # Calcul du statut
                if prog and prog.completed_at:
                    status = "done"
                elif asgn.due_date and now > asgn.due_date:
                    status = "late"
                elif prog and prog.cards_reviewed > 0:
                    status = "in_progress"
                else:
                    status = "todo"

                result.append(AssignmentSummarySchema(
                    id=asgn.id,
                    group_id=asgn.group_id,
                    group_name=group.name if group else "",
                    binder_id=asgn.binder_id,
                    binder_name=self._binder_name(asgn.binder_id),
                    title=asgn.title,
                    description=asgn.description,
                    due_date=asgn.due_date,
                    created_at=asgn.created_at,
                    my_cards_reviewed=prog.cards_reviewed if prog else 0,
                    my_score_pct=prog.score_pct if prog else None,
                    my_completed_at=prog.completed_at if prog else None,
                    status=status
                ))

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
                card_ids = get_all_card_ids_in_binder(db.session, binder.id)
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
            
        children = db_session.query(Binder.id).filter_by(parent_id=b_id).all()
        for child_id_tup in children:
            collect_cards(child_id_tup[0])
            
    collect_cards(binder_id)
    return card_ids


def update_assignment_progress(db_session, user_id: int, assignment_id: int):
    assignment = db_session.get(Assignment, assignment_id)
    if not assignment:
        return
        
    card_ids = get_all_card_ids_in_binder(db_session, assignment.binder_id)
    total_cards = len(card_ids)
    
    if total_cards == 0:
        progress = db_session.get(AssignmentProgress, (assignment_id, user_id))
        if not progress:
            progress = AssignmentProgress(assignment_id=assignment_id, user_id=user_id)
            db_session.add(progress)
        progress.cards_reviewed = 0
        progress.score_pct = 100.0
        if not progress.completed_at:
            progress.completed_at = datetime.utcnow()
        db_session.commit()
        return

    from app.models.study_session import StudySession
    
    sessions = (
        db_session.query(StudySession)
        .filter(
            StudySession.user_id == user_id,
            StudySession.module == "flashcard",
            StudySession.flashcard_id.in_(card_ids),
            StudySession.created_at >= assignment.created_at - timedelta(seconds=5)
        )
        .all()
    )
    
    reviewed_card_ids = {s.flashcard_id for s in sessions if s.flashcard_id}
    unique_reviewed = len(reviewed_card_ids)
    
    total_reviewed = sum(s.cards_reviewed or 0 for s in sessions)
    total_correct = sum(s.cards_correct or 0 for s in sessions)
    score_pct = (total_correct / total_reviewed * 100.0) if total_reviewed > 0 else 0.0
    
    progress = db_session.get(AssignmentProgress, (assignment_id, user_id))
    if not progress:
        progress = AssignmentProgress(assignment_id=assignment_id, user_id=user_id)
        db_session.add(progress)
        
    progress.cards_reviewed = unique_reviewed
    progress.score_pct = score_pct
    
    if unique_reviewed >= total_cards:
        if not progress.completed_at:
            progress.completed_at = datetime.utcnow()
    else:
        progress.completed_at = None
        
    db_session.commit()


def trigger_assignment_progress_update(db_session, user_id: int, card_id: int):
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
        
    from app.models.assignment import Assignment
    from app.models.group import GroupMember
    
    assignments = (
        db_session.query(Assignment)
        .join(GroupMember, Assignment.group_id == GroupMember.group_id)
        .filter(
            GroupMember.user_id == user_id,
            Assignment.binder_id.in_(binder_ids)
        )
        .all()
    )
    
    for asgn in assignments:
        update_assignment_progress(db_session, user_id, asgn.id)
