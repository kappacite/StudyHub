from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.group import Group, GroupMember, GroupBinder, GroupActivity
from app.dao.base_dao import BaseDAO

class GroupDAO(BaseDAO[Group]):
    def __init__(self, db: Session):
        super().__init__(Group, db)

    def get_by_invite_code(self, invite_code: str) -> Optional[Group]:
        return self.db.query(self.model).filter_by(invite_code=invite_code).first()

    def get_user_groups(self, user_id: int) -> List[Group]:
        # Récupère tous les groupes dont l'utilisateur est membre
        return (
            self.db.query(self.model)
            .join(GroupMember, GroupMember.group_id == self.model.id)
            .filter(GroupMember.user_id == user_id)
            .all()
        )

    def count_user_created_groups(self, user_id: int) -> int:
        return self.db.query(self.model).filter_by(created_by=user_id).count()

    def count_user_joined_groups(self, user_id: int) -> int:
        return (
            self.db.query(GroupMember)
            .filter_by(user_id=user_id)
            .count()
        )

    # --- GroupMember ---
    def get_group_member(self, group_id: int, user_id: int) -> Optional[GroupMember]:
        return (
            self.db.query(GroupMember)
            .filter_by(group_id=group_id, user_id=user_id)
            .first()
        )

    def get_group_members(self, group_id: int) -> List[GroupMember]:
        return (
            self.db.query(GroupMember)
            .filter_by(group_id=group_id)
            .all()
        )

    def add_group_member(self, group_id: int, user_id: int, role: str) -> GroupMember:
        member = GroupMember(group_id=group_id, user_id=user_id, role=role)
        self.db.add(member)
        self.db.commit()
        return member

    def remove_group_member(self, member: GroupMember) -> None:
        self.db.delete(member)
        self.db.commit()

    def update_group_member(self, member: GroupMember) -> GroupMember:
        self.db.commit()
        return member

    # --- GroupBinder ---
    def get_group_binder(self, group_id: int, binder_id: int) -> Optional[GroupBinder]:
        return (
            self.db.query(GroupBinder)
            .filter_by(group_id=group_id, binder_id=binder_id)
            .first()
        )

    def get_group_binders(self, group_id: int) -> List[GroupBinder]:
        return (
            self.db.query(GroupBinder)
            .filter_by(group_id=group_id)
            .all()
        )

    def add_group_binder(self, group_id: int, binder_id: int, permission: str, added_by: int) -> GroupBinder:
        group_binder = GroupBinder(
            group_id=group_id,
            binder_id=binder_id,
            permission=permission,
            added_by=added_by
        )
        self.db.add(group_binder)
        self.db.commit()
        return group_binder

    def remove_group_binder(self, group_binder: GroupBinder) -> None:
        self.db.delete(group_binder)
        self.db.commit()

    # --- GroupActivity ---
    def get_group_activities(self, group_id: int, limit: int = 50, offset: int = 0) -> List[GroupActivity]:
        return (
            self.db.query(GroupActivity)
            .filter_by(group_id=group_id)
            .order_by(GroupActivity.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

    def add_group_activity(self, group_id: int, user_id: int, activity_type: str, payload: dict = None) -> GroupActivity:
        activity = GroupActivity(
            group_id=group_id,
            user_id=user_id,
            type=activity_type,
            payload=payload
        )
        self.db.add(activity)
        self.db.commit()
        return activity
