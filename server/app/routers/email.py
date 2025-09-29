from fastapi import APIRouter
from typing import Annotated

from fastapi import Response, Depends, HTTPException, status, Request
from sqlmodel import select

from app.config import get_settings
from app.db.connection import SessionDep
from app.dependencies import get_current_user
from app.schemas.app import User, BaseEmail, Email
from app.services.email import gmail_create_draft, gmail_send_draft

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

@router.get("/emails")
def get_emails(
        current_user: Annotated[User, Depends(get_current_user)],
        session: SessionDep
) -> list[Email]:
    return session.exec(select(Email)
                        .where(Email.user_id == current_user.user_id)).all()

@router.post("/emails/create_draft")
def create_draft(
        current_user: Annotated[User, Depends(get_current_user)],
        to: str,
        subject: str,
        body: str
):
    return gmail_create_draft(current_user, subject, body, to)

@router.post("/emails/send_draft")
def send_draft(
        current_user: Annotated[User, Depends(get_current_user)],
        draft_id: str
):
    gmail_send_draft(current_user, draft_id)
    return {"message": "Draft sent"}

@router.post("/emails/send_directly")
def send_draft(
        current_user: Annotated[User, Depends(get_current_user)],
        to: str,
        subject: str,
        body: str
):
    draft = gmail_create_draft(current_user, subject, body, to)
    gmail_send_draft(current_user, draft["id"])
    return {"message": "Message sent"}