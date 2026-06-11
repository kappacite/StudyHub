import string
import secrets
from datetime import datetime, timedelta, timezone
from typing import List, Tuple, Optional
from sqlalchemy import func

from app.dao.group_dao import GroupDAO
from app.dao.binder_dao import BinderDAO
from app.dao.user_dao import UserDAO
from app.models.group import Group, GroupMember, GroupBinder, GroupActivity
from app.models.study_session import StudySession
from app.schemas.group_schema import (
    GroupCreateSchema, GroupResponseSchema, GroupDetailResponseSchema,
    GroupMemberResponseSchema, GroupBinderResponseSchema, GroupActivityResponseSchema,
    GroupMemberProgressSchema
)
from app.middlewares.error_handler import ResourceNotFoundError, ForbiddenError, ConflictError

class GroupService:
    def __init__(self, group_dao: GroupDAO, binder_dao: BinderDAO, user_dao: UserDAO):
        self._group_dao = group_dao
        self._binder_dao = binder_dao
        self._user_dao = user_dao

    def _generate_invite_code(self) -> str:
        alphabet = string.ascii_uppercase + string.digits
        for _ in range(50):  # Limiter les essais pour éviter une boucle infinie
            code = ''.join(secrets.choice(alphabet) for _ in range(8))
            if not self._group_dao.get_by_invite_code(code):
                return code
        raise ConflictError("Impossible de générer un code d'invitation unique.")

    def _check_membership(self, group_id: int, user_id: int) -> GroupMember:
        member = self._group_dao.get_group_member(group_id, user_id)
        if not member:
            raise ForbiddenError("Vous n'êtes pas membre de ce groupe.")
        return member

    def create_group(self, user_id: int, data: GroupCreateSchema) -> GroupResponseSchema:
        # Règle : un utilisateur peut créer max 5 groupes
        created_count = self._group_dao.count_user_created_groups(user_id)
        if created_count >= 5:
            raise ForbiddenError("Vous ne pouvez pas créer plus de 5 groupes.")

        # Règle : un utilisateur peut appartenir à max 20 groupes
        joined_count = self._group_dao.count_user_joined_groups(user_id)
        if joined_count >= 20:
            raise ForbiddenError("Vous ne pouvez pas appartenir à plus de 20 groupes.")

        invite_code = self._generate_invite_code()
        group = Group(
            name=data.name,
            description=data.description,
            invite_code=invite_code,
            created_by=user_id
        )
        created = self._group_dao.create(group)

        # Ajouter le créateur comme propriétaire (owner)
        self._group_dao.add_group_member(created.id, user_id, "owner")

        # Tracer l'activité
        self._group_dao.add_group_activity(created.id, user_id, "joined")

        return GroupResponseSchema(
            id=created.id,
            name=created.name,
            description=created.description,
            invite_code=created.invite_code,
            created_by=created.created_by,
            created_at=created.created_at,
            members_count=1,
            binders_count=0
        )

    def get_my_groups(self, user_id: int) -> List[GroupResponseSchema]:
        groups = self._group_dao.get_user_groups(user_id)
        response = []
        for g in groups:
            if g.is_class:
                continue
            members_count = len(g.members_assoc)
            binders_count = len(g.binders_assoc)
            response.append(
                GroupResponseSchema(
                    id=g.id,
                    name=g.name,
                    description=g.description,
                    invite_code=g.invite_code,
                    created_by=g.created_by,
                    created_at=g.created_at,
                    members_count=members_count,
                    binders_count=binders_count
                )
            )
        return response

    def get_group_detail(self, group_id: int, user_id: int) -> GroupDetailResponseSchema:
        group = self._group_dao.get_by_id(group_id)
        if not group:
            raise ResourceNotFoundError("Groupe introuvable.")
        
        self._check_membership(group_id, user_id)

        # Formater les membres
        members = []
        for assoc in group.members_assoc:
            user = assoc.user
            members.append(
                GroupMemberResponseSchema(
                    user_id=assoc.user_id,
                    username=user.username,
                    email=user.email,
                    role=assoc.role,
                    joined_at=assoc.joined_at
                )
            )

        # Formater les classeurs
        binders = []
        for assoc in group.binders_assoc:
            binder = assoc.binder
            binders.append(
                GroupBinderResponseSchema(
                    group_id=assoc.group_id,
                    binder_id=assoc.binder_id,
                    binder_name=binder.name,
                    permission=assoc.permission,
                    pinned=assoc.pinned,
                    added_by=assoc.added_by,
                    added_at=assoc.added_at
                )
            )

        return GroupDetailResponseSchema(
            id=group.id,
            name=group.name,
            description=group.description,
            invite_code=group.invite_code,
            created_by=group.created_by,
            created_at=group.created_at,
            members=members,
            binders=binders
        )

    def join_group(self, user_id: int, invite_code: str) -> GroupResponseSchema:
        # Règle : max 20 groupes rejoints
        joined_count = self._group_dao.count_user_joined_groups(user_id)
        if joined_count >= 20:
            raise ForbiddenError("Vous ne pouvez pas appartenir à plus de 20 groupes.")

        group = self._group_dao.get_by_invite_code(invite_code)
        if not group:
            raise ResourceNotFoundError("Code d'invitation invalide.")

        # Vérifier si déjà membre
        existing = self._group_dao.get_group_member(group.id, user_id)
        if existing:
            raise ConflictError("Vous êtes déjà membre de ce groupe.")

        self._group_dao.add_group_member(group.id, user_id, "member")

        # Tracer l'activité
        self._group_dao.add_group_activity(group.id, user_id, "joined")

        members_count = len(group.members_assoc)
        binders_count = len(group.binders_assoc)

        return GroupResponseSchema(
            id=group.id,
            name=group.name,
            description=group.description,
            invite_code=group.invite_code,
            created_by=group.created_by,
            created_at=group.created_at,
            members_count=members_count,
            binders_count=binders_count
        )

    def leave_or_exclude_member(self, group_id: int, target_user_id: int, request_user_id: int) -> None:
        group = self._group_dao.get_by_id(group_id)
        if not group:
            raise ResourceNotFoundError("Groupe introuvable.")

        # Récupérer l'appartenance du demandeur et de la cible
        req_member = self._check_membership(group_id, request_user_id)
        target_member = self._group_dao.get_group_member(group_id, target_user_id)
        if not target_member:
            raise ResourceNotFoundError("Le membre ciblé ne fait pas partie du groupe.")

        if target_user_id == request_user_id:
            # L'utilisateur souhaite quitter le groupe de son plein gré
            if target_member.role == "owner":
                # Le propriétaire ne peut pas quitter le groupe s'il reste d'autres membres
                other_members = len(group.members_assoc) > 1
                if other_members:
                    raise ConflictError("Vous devez transférer la propriété du groupe avant de le quitter.")
                else:
                    # Seul membre, on supprime tout le groupe
                    self._group_dao.delete(group)
                    return
            
            self._group_dao.remove_group_member(target_member)
        else:
            # C'est une exclusion
            # Vérifier que le demandeur a les droits requis
            if req_member.role == "owner":
                # Le propriétaire peut tout faire
                pass
            elif req_member.role == "admin":
                # Un admin ne peut exclure que des membres simples
                if target_member.role in ("owner", "admin"):
                    raise ForbiddenError("Vous ne pouvez pas exclure un administrateur ou le propriétaire du groupe.")
            else:
                raise ForbiddenError("Vous n'avez pas les droits requis pour exclure des membres.")

            self._group_dao.remove_group_member(target_member)

    def update_member_role(self, group_id: int, target_user_id: int, request_user_id: int, new_role: str) -> GroupMemberResponseSchema:
        group = self._group_dao.get_by_id(group_id)
        if not group:
            raise ResourceNotFoundError("Groupe introuvable.")

        req_member = self._check_membership(group_id, request_user_id)
        target_member = self._group_dao.get_group_member(group_id, target_user_id)
        if not target_member:
            raise ResourceNotFoundError("Le membre ciblé ne fait pas partie du groupe.")

        # Seul le propriétaire peut changer les rôles
        if req_member.role != "owner":
            raise ForbiddenError("Seul le propriétaire du groupe peut modifier les rôles.")

        if target_user_id == request_user_id:
            raise ConflictError("Vous ne pouvez pas modifier votre propre rôle.")

        target_member.role = new_role
        updated = self._group_dao.update_group_member(target_member)
        user = updated.user

        return GroupMemberResponseSchema(
            user_id=updated.user_id,
            username=user.username,
            email=user.email,
            role=updated.role,
            joined_at=updated.joined_at
        )

    def share_binder(self, group_id: int, user_id: int, binder_id: int, permission: str) -> GroupBinderResponseSchema:
        group = self._group_dao.get_by_id(group_id)
        if not group:
            raise ResourceNotFoundError("Groupe introuvable.")

        self._check_membership(group_id, user_id)

        # Vérifier que le classeur appartient à l'utilisateur
        binder = self._binder_dao.get_by_id(binder_id)
        if not binder or binder.user_id != user_id:
            raise ForbiddenError("Vous ne pouvez partager que vos propres classeurs.")

        # Vérifier si déjà partagé
        existing = self._group_dao.get_group_binder(group_id, binder_id)
        if existing:
            raise ConflictError("Ce classeur est déjà partagé dans ce groupe.")

        created = self._group_dao.add_group_binder(group_id, binder_id, permission, user_id)

        # Enregistrer l'activité
        self._group_dao.add_group_activity(
            group_id,
            user_id,
            "shared_binder",
            payload={"binder_id": binder_id, "binder_name": binder.name}
        )

        return GroupBinderResponseSchema(
            group_id=created.group_id,
            binder_id=created.binder_id,
            binder_name=binder.name,
            permission=created.permission,
            pinned=created.pinned,
            added_by=created.added_by,
            added_at=created.added_at
        )

    def unshare_binder(self, group_id: int, user_id: int, binder_id: int) -> None:
        group = self._group_dao.get_by_id(group_id)
        if not group:
            raise ResourceNotFoundError("Groupe introuvable.")

        req_member = self._check_membership(group_id, user_id)
        group_binder = self._group_dao.get_group_binder(group_id, binder_id)
        if not group_binder:
            raise ResourceNotFoundError("Ce classeur n'est pas partagé dans ce groupe.")

        # Autorisation de supprimer le partage :
        # - L'utilisateur qui l'a partagé (added_by == user_id)
        # - Le propriétaire du classeur d'origine (binder.user_id == user_id)
        # - Le propriétaire ou admin du groupe
        is_creator = group_binder.added_by == user_id
        is_binder_owner = group_binder.binder.user_id == user_id
        is_group_admin = req_member.role in ("owner", "admin")

        if not (is_creator or is_binder_owner or is_group_admin):
            raise ForbiddenError("Vous n'êtes pas autorisé à retirer ce classeur du groupe.")

        self._group_dao.remove_group_binder(group_binder)

    def get_group_activity(self, group_id: int, user_id: int, page: int = 1, per_page: int = 50) -> List[GroupActivityResponseSchema]:
        group = self._group_dao.get_by_id(group_id)
        if not group:
            raise ResourceNotFoundError("Groupe introuvable.")

        self._check_membership(group_id, user_id)

        offset = (page - 1) * per_page
        activities = self._group_dao.get_group_activities(group_id, limit=per_page, offset=offset)

        response = []
        for act in activities:
            user = act.user
            response.append(
                GroupActivityResponseSchema(
                    id=act.id,
                    user_id=act.user_id,
                    username=user.username,
                    type=act.type,
                    payload=act.payload,
                    created_at=act.created_at
                )
            )
        return response

    def get_group_members_progress(self, group_id: int, user_id: int) -> List[GroupMemberProgressSchema]:
        group = self._group_dao.get_by_id(group_id)
        if not group:
            raise ResourceNotFoundError("Groupe introuvable.")

        self._check_membership(group_id, user_id)

        # Plage des 7 derniers jours
        start_date = datetime.utcnow() - timedelta(days=7)

        progress_list = []
        for assoc in group.members_assoc:
            member_user = assoc.user
            
            # Requête agrégée sur StudySession
            sessions = (
                self._group_dao.db.query(
                    func.sum(StudySession.duration_seconds).label("total_time"),
                    func.sum(StudySession.cards_reviewed).label("reviewed"),
                    func.sum(StudySession.cards_correct).label("correct")
                )
                .filter(
                    StudySession.user_id == member_user.id,
                    StudySession.created_at >= start_date
                )
                .first()
            )

            progress_list.append(
                GroupMemberProgressSchema(
                    user_id=member_user.id,
                    username=member_user.username,
                    total_time_seconds=int(sessions.total_time or 0),
                    cards_reviewed=int(sessions.reviewed or 0),
                    cards_correct=int(sessions.correct or 0)
                )
            )

        # Trier par temps d'étude décroissant
        progress_list.sort(key=lambda x: x.total_time_seconds, reverse=True)
        return progress_list
