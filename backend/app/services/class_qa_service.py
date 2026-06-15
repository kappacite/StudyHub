"""ClassQAService — questions des élèves au professeur (B4).

Un élève poste une question ; le professeur y répond (ce qui la clôt). Des
notifications in-app préviennent les professeurs (nouvelle question) et l'élève
(réponse reçue). Isolation : un élève ne voit que ses propres questions ; le
professeur voit toutes celles de sa classe.
"""
from datetime import datetime
from typing import List

from app.dao.group_dao import GroupDAO
from app.models.group import Group, GroupMember
from app.models.user import User
from app.models.notification import Notification
from app.models.class_question import ClassQuestion
from app.schemas.engagement_schema import (
    ClassQuestionCreateSchema, ClassQuestionAnswerSchema, ClassQuestionResponseSchema,
)
from app.middlewares.error_handler import ResourceNotFoundError, ForbiddenError


class ClassQAService:
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

    def _is_teacher(self, member: GroupMember) -> bool:
        return member.role in ("owner", "admin")

    def _teacher_ids(self, class_id: int) -> List[int]:
        rows = (
            self._db.query(GroupMember.user_id)
            .filter(GroupMember.group_id == class_id,
                    GroupMember.role.in_(("owner", "admin")))
            .all()
        )
        return [r[0] for r in rows]

    def _serialize(self, q: ClassQuestion) -> ClassQuestionResponseSchema:
        return ClassQuestionResponseSchema(
            id=q.id, body=q.body, answer=q.answer, status=q.status,
            author_id=q.author_id,
            author_username=q.author.username if q.author else None,
            answered_by_username=q.answerer.username if q.answerer else None,
            created_at=q.created_at, answered_at=q.answered_at,
        )

    # ─── Actions ──────────────────────────────────────────────────────────────

    def post_question(self, class_id: int, user_id: int,
                      data: ClassQuestionCreateSchema) -> ClassQuestionResponseSchema:
        self._get_class_or_404(class_id)
        self._require_membership(class_id, user_id)

        q = ClassQuestion(group_id=class_id, author_id=user_id, body=data.body, status="open")
        self._db.add(q)
        self._db.flush()

        # Notifier les professeurs de la classe.
        author = self._db.get(User, user_id)
        author_name = author.username if author else "Un élève"
        for tid in self._teacher_ids(class_id):
            if tid == user_id:
                continue
            self._db.add(Notification(
                user_id=tid, type="question", group_id=class_id,
                title=f"Nouvelle question de {author_name}",
                body=data.body[:200], link="/classes/teacher",
            ))
        self._db.commit()
        self._db.refresh(q)
        return self._serialize(q)

    def list_questions(self, class_id: int, user_id: int) -> List[ClassQuestionResponseSchema]:
        self._get_class_or_404(class_id)
        member = self._require_membership(class_id, user_id)

        query = self._db.query(ClassQuestion).filter(ClassQuestion.group_id == class_id)
        if not self._is_teacher(member):
            # Un élève ne voit que ses propres questions.
            query = query.filter(ClassQuestion.author_id == user_id)
        rows = query.order_by(ClassQuestion.created_at.desc(), ClassQuestion.id.desc()).all()
        return [self._serialize(q) for q in rows]

    def answer_question(self, class_id: int, teacher_id: int, question_id: int,
                        data: ClassQuestionAnswerSchema) -> ClassQuestionResponseSchema:
        self._get_class_or_404(class_id)
        member = self._require_membership(class_id, teacher_id)
        if not self._is_teacher(member):
            raise ForbiddenError("Seul un professeur peut répondre aux questions.")

        q = self._db.get(ClassQuestion, question_id)
        if not q or q.group_id != class_id:
            raise ResourceNotFoundError("Question introuvable.")

        q.answer = data.body
        q.answered_by = teacher_id
        q.status = "answered"
        q.answered_at = datetime.utcnow()

        # Notifier l'auteur de la question.
        self._db.add(Notification(
            user_id=q.author_id, type="answer", group_id=class_id,
            title="Votre question a une réponse",
            body=data.body[:200], link="/classes/student",
        ))
        self._db.commit()
        self._db.refresh(q)
        return self._serialize(q)
