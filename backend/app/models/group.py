from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.extensions import db
from typing import Optional

class Group(db.Model):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    invite_code = Column(String(8), unique=True, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    type = Column(String(10), default="study", nullable=False)       # "study" | "class"
    is_class = Column(Boolean, default=False, nullable=False)        # shortcut
    is_public = Column(Boolean, default=False, nullable=False)


    # Relations
    owner = relationship("User", foreign_keys=[created_by])
    members_assoc = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")
    binders_assoc = relationship("GroupBinder", back_populates="group", cascade="all, delete-orphan")
    activities = relationship("GroupActivity", back_populates="group", cascade="all, delete-orphan")
    assignments = relationship("Assignment", back_populates="group", cascade="all, delete-orphan")

class GroupMember(db.Model):
    __tablename__ = "group_members"

    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role = Column(String(10), nullable=False)  # "owner" | "admin" | "member"
    joined_at = Column(DateTime, server_default=func.now())

    # Relations
    group = relationship("Group", back_populates="members_assoc")
    user = relationship("User")

class GroupBinder(db.Model):
    __tablename__ = "group_binders"

    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True)
    binder_id = Column(Integer, ForeignKey("binders.id", ondelete="CASCADE"), primary_key=True)
    permission = Column(String(10), nullable=False)  # "read" | "write"
    pinned = Column(Boolean, default=False, nullable=False)
    added_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    added_at = Column(DateTime, server_default=func.now())

    # Relations
    group = relationship("Group", back_populates="binders_assoc")
    binder = relationship("Binder")
    added_by_user = relationship("User", foreign_keys=[added_by])

    @property
    def binder_uuid(self) -> Optional[str]:
        return self.binder.id if self.binder else None

class GroupActivity(db.Model):
    __tablename__ = "group_activities"

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(30), nullable=False)  # "joined" | "shared_binder" | "completed_session" | "posted_note"
    payload = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relations
    group = relationship("Group", back_populates="activities")
    user = relationship("User")
