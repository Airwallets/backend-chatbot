import base64
from email.message import EmailMessage

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from app.config import get_settings
import requests

from app.schemas.app import User
from ..routers.oauth import SCOPES

def get_credentials(user: User) -> Credentials:
  settings = get_settings()
  creds = Credentials(
    token=user.access_token,
    token_uri="https://oauth2.googleapis.com/token",
    refresh_token=user.refresh_token,
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    scopes=" ".join(SCOPES)
  )
  return creds

def refresh_google_token(refresh_token: str):
  data = {
    "client_id": get_settings().google_client_id,
    "client_secret": get_settings().google_client_secret,
    "refresh_token": refresh_token,
    "grant_type": "refresh_token",
  }
  response = requests.post("https://oauth2.googleapis.com/token", data=data)
  response.raise_for_status()
  return response.json()["access_token"]  # contains new access_token (and expiry)


def gmail_create_draft(user: User, subject: str, body: str, to: str):
  """Create and insert a draft email.
   Print the returned draft's message and id.
   Returns: Draft object, including draft id and message meta data.

  """
  creds = get_credentials(user)

  try:
    # create gmail api client
    service = build("gmail", "v1", credentials=creds)

    message = EmailMessage()

    message.set_content(body)

    message["To"] = to
    message["From"] = user.email
    message["Subject"] = subject

    # encoded message
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    create_message = {"message": {"raw": encoded_message}}
    # pylint: disable=E1101
    draft = (
        service.users()
        .drafts()
        .create(userId="me", body=create_message)
        .execute()
    )

    print(f'Draft id: {draft["id"]}\nDraft message: {draft["message"]}')

  except HttpError as error:
    print(f"An error occurred: {error}")
    draft = None

  return draft

def gmail_send_draft(user: User, draft_id: str):
  """Send an existing draft email by its ID."""
  creds = get_credentials(user)
  try:
    service = build("gmail", "v1", credentials=creds)
    sent_message = (
      service.users()
      .drafts()
      .send(userId="me", body={"id": draft_id})
      .execute()
    )
    print(f'Sent message ID: {sent_message["id"]}')
  except HttpError as error:
    print(f"An error occurred: {error}")