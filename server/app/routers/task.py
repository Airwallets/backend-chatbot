from fastapi import APIRouter
from typing import Annotated

from fastapi import Response, Depends, HTTPException, status, Request
from uuid import UUID
from app.config import get_settings
from app.db.connection import SessionDep
from app.dependencies import get_current_user
from app.schemas.app import User, Task

from app.services.task import get_tasks_by_user

router = APIRouter(tags=["task"])


@router.post("/task")
def add_task(
    current_user: Annotated[User, Depends(get_current_user)],
    session: SessionDep,
    title: str,
    description: str,
    email_id: UUID
) -> Task:
    """
    Add tasks
    """

    new_task = Task(title=title, description=description, email_id=email_id)
    session.add(new_task)
    session.commit()
    return {"message": "success"}

@router.get("/task")
def get_tasks(
    current_user: Annotated[User, Depends(get_current_user)],
    session: SessionDep
) -> list[Task]:
    return get_tasks_by_user(current_user, session)
