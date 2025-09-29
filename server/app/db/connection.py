from typing import Annotated

from fastapi import Depends
from sqlmodel import create_engine, Session
from app.config import get_settings


def get_sqlmodel_engine():
    """
    Returns a sqlmodel engine connection
    :return:
    """
    settings = get_settings()

    return create_engine(
        f"postgresql://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:5432/{settings.postgres_db}",
    )


def get_sqlmodel_session():
    """
    Yields the sqlmodel engine session
    """
    with Session(get_sqlmodel_engine()) as session:
        yield session


# Alias for session dependency since it is so common
SessionDep = Annotated[Session, Depends(get_sqlmodel_session)]
