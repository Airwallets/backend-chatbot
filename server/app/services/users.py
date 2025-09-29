import uuid

from sqlmodel import select, Session

from app.db.connection import SessionDep
from app.models.api import ConversationRequest, SortingOrder
from app.schemas.app import (
    User,
    Role,
    ServiceSuggestion,
    RoleType,
    SuspiciousActivity,
    UserStatus,
    Conversation,
)
from pydantic import BaseModel
from sqlalchemy import func, asc, desc
from sqlalchemy.orm import selectinload


def init_roles(session: SessionDep):
    """
    Create initial app roles
    """
    for role in RoleType:
        check_exist = session.exec(
            select(Role).where(Role.type == role)
        ).first()
        if check_exist is None:
            role_entry = Role(type=role)
            session.add(role_entry)
    session.commit()


def find_one(session: SessionDep, email: str) -> User | None:
    """
    Finds a user by email
    """
    return session.exec(select(User).where(User.email == email)).first()


def add_one(session: SessionDep, user: User):
    """
    Adds a user to the database
    """
    session.add(user)
    session.commit()
