from datetime import datetime, timedelta, timezone
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from ..schemas.app import User
from ..config import get_settings
from ..routers.oauth import SCOPES

# Load credentials (must include https://www.googleapis.com/auth/calendar scope)

def create_google_api_client(service, user: User):
    settings = get_settings()
    creds = Credentials(
        token=user.access_token,
        token_uri="https://oauth2.googleapis.com/token",
        refresh_token=user.refresh_token,
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        scopes=SCOPES
    )
    service = build(service, "v3", credentials=creds)
    return service

def create_calendar_event(client, title, email, start_time):
    # Event details
    end_time = start_time + timedelta(hours=1)

    event = {
        "summary": title,
        "start": {
            "dateTime": start_time.isoformat() + "Z",  # UTC
            "timeZone": "Australia/Sydney",
        },
        "end": {
            "dateTime": end_time.isoformat() + "Z",
            "timeZone": "Australia/Sydney",
        },
        "attendees": [
            {"email": email}
        ],
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "email", "minutes": 24 * 60},  # 1 day before
                {"method": "popup", "minutes": 10},       # 10 mins before
            ],
        },
    }

    # Insert event & send invitations
    event_result = (
        client.events()
        .insert(
            calendarId="primary", 
            body=event, 
            sendUpdates="all"   # ensures invites are emailed
        )
        .execute()
    )

