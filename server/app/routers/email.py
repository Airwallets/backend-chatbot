from fastapi import APIRouter
from typing import Annotated

from fastapi import Response, Depends, HTTPException, status, Request

from app.config import get_settings
from app.db.connection import SessionDep
from app.dependencies import get_current_user
from app.schemas.app import User, BaseEmail, Email

router = APIRouter(tags=["email"])


@router.post("/emails/add_email")
async def add_email(
    current_user: Annotated[User, Depends(get_current_user)],
    session: SessionDep,
    email: BaseEmail
) -> Email:
    """
    Retrieves the currently logged in user
    """

    new_email = Email(**email.model_dump(), user_id=current_user.user_id)
    session.add(new_email)
    session.commit()
    session.refresh(new_email)
    return new_email
