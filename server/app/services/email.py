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


def gmail_list_messages(service, user_id="me", label_ids=None, query=None, max_results=100):
    """
    List message IDs in the user’s mailbox.
    Returns a list of message dicts with “id” and “threadId”.
    """
    try:
        request = service.users().messages().list(
            userId=user_id,
            labelIds=label_ids,
            q=query,
            maxResults=max_results
        )
        response = request.execute()
        return response.get("messages", [])
    except HttpError as error:
        print(f"An error occurred listing messages: {error}")
        return []

def gmail_get_message(service, msg_id, user_id="me", format="full"):
    """
    Fetch a message by ID.
    format can be "full", "raw", "metadata", or "minimal".
    Returns the message resource dict.
    """
    try:
        message = service.users().messages().get(
            userId=user_id,
            id=msg_id,
            format=format
        ).execute()
        return message
    except HttpError as error:
        print(f"An error occurred fetching message {msg_id}: {error}")
        return None

def parse_message_body(message):
    """
    Given a message (as returned with format="full"), extract the body text.
    Handles multipart and simple text messages.
    Returns a dict like {"text": ..., "html": ...}.
    """
    payload = message.get("payload", {})
    parts = payload.get("parts")
    body_text = None
    body_html = None

    def _decode_part(part):
        data = part.get("body", {}).get("data")
        if not data:
            return None
        decoded = base64.urlsafe_b64decode(data.encode("UTF-8"))
        try:
            return decoded.decode("utf-8")
        except UnicodeDecodeError:
            return decoded.decode("latin-1", errors="ignore")

    if parts:
        # multipart message, iterate parts
        for part in parts:
            mime_type = part.get("mimeType", "")
            if mime_type == "text/plain":
                body_text = _decode_part(part)
            elif mime_type == "text/html":
                body_html = _decode_part(part)
    else:
        # not multipart, maybe body directly
        body_text = _decode_part(payload)

    return {"text": body_text, "html": body_html}

def gmail_read_inbox(user: User, max_msgs=10, label_ids=None, query="is:unread"):
    """
    Top-level function to list and read recent messages for a given user.
    """
    creds = get_credentials(user)
    service = build("gmail", "v1", credentials=creds)

    if label_ids is None:
      label_ids = ["INBOX"]

    msgs = gmail_list_messages(service, user_id="me", label_ids=label_ids, query=query, max_results=max_msgs)
    results = []
    for m in msgs:
        msg_id = m["id"]
        full = gmail_get_message(service, msg_id, format="full")
        if not full:
            continue
        snippet = full.get("snippet")
        headers = full.get("payload", {}).get("headers", [])
        # extract subject, from, to, etc.
        header_map = {h.get("name"): h.get("value") for h in headers}
        body = parse_message_body(full)
        results.append({
            "id": msg_id,
            "snippet": snippet,
            "headers": header_map,
            "body": body
        })
    return results