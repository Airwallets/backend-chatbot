import uuid

from sqlmodel import select, Session

from app.db.connection import SessionDep
from app.schemas.app import (
    User
)


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
