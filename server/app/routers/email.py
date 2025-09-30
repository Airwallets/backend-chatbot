from datetime import datetime
from fastapi import APIRouter
from typing import Annotated

from fastapi import Response, Depends, HTTPException, status, Request
from sqlmodel import select

from app.config import get_settings
from app.db.connection import SessionDep
from app.dependencies import get_current_user
from app.schemas.app import User, BaseEmail, Email
from app.services.email import gmail_create_draft, gmail_send_draft, gmail_read_inbox

from app.services.chatbot.email import get_ai_summary, get_ai_draft, Summary, Draft

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

@router.post("/emails/gen_ai_summary")
def gen_ai_summary(
    message: str
) -> Summary:
    return get_ai_summary(message)

@router.post("/emails/gen_ai_draft")
def gen_ai_draft(
    message: str
) -> Draft:
    return get_ai_draft(message)

@router.post("/emails/get_emails")
def get_gmail_emails(
    current_user: Annotated[User, Depends(get_current_user)],
    session: SessionDep,
    label_ids: list[str] = None,
    query: str = "is:unread"
) -> list[Email]:
    emails = gmail_read_inbox(current_user, label_ids = label_ids, query = query)
    result = []
    for email in emails:
        parsed = Email(
            from_sender = email["headers"]["From"],
            email_subject = email["headers"]["Subject"],
            email_status="unread",
            email_timestamp=datetime.strptime(email["headers"]["Date"], "%a, %d %b %Y %H:%M:%S %z"),
            full_content=email["body"]["text"],
            user_id=current_user.user_id
        )
        session.add(parsed)
        session.commit()
        session.refresh(parsed)
        result.append(parsed.model_copy())
    return result