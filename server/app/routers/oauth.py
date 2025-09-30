from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse, JSONResponse, Response

from typing import Annotated
from urllib.parse import urlencode
from datetime import timedelta

from ..db.connection import SessionDep
from ..services.users import find_one, add_one
from ..services.auth import signup_user, UserSignup, create_access_token

from ..schemas.app import User
from ..dependencies import get_current_user

import requests

from ..config import get_settings

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

router = APIRouter()

SCOPES = [
    "openid",
    "email",
    "profile",
    "https://www.googleapis.com/auth/calendar",       # full calendar access
    "https://mail.google.com/"  # gmail full access
]

@router.get("/oauth/login")
async def login():
    params = {
        "client_id": get_settings().google_client_id,
        "redirect_uri": get_settings().google_redirect_uri,
        "response_type": "code",
        "scope": " ".join(SCOPES),  # add more scopes if needed
        "access_type": "offline",  # ensures refresh token
        "prompt": "consent",       # ensures prompt each time
    }
    url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    return RedirectResponse(url)

@router.get("/callback")
async def oauth_callback(session: SessionDep, code: str):
    # Exchange code for tokens
    data = {
        "code": code,
        "client_id": get_settings().google_client_id,
        "client_secret": get_settings().google_client_secret,
        "redirect_uri": get_settings().google_redirect_uri,
        "grant_type": "authorization_code",
    } 
    token_response = requests.post(GOOGLE_TOKEN_URL, data=data)
    token_json = token_response.json()

    # Use access token to fetch user info
    access_token = token_json["access_token"]
    refresh_token = token_json["refresh_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    userinfo_response = requests.get(GOOGLE_USERINFO_URL, headers=headers)
    userinfo = userinfo_response.json()
    email = userinfo["email"]
    first_name = userinfo["given_name"]
    last_name = userinfo["family_name"]

    user = find_one(session, email)

    if user is None:
        user = signup_user(session, UserSignup(email=email, name=f"{first_name} {last_name}", password="abcdefg"))
        user.access_token = access_token
        user.refresh_token = refresh_token
        session.add(user)
        session.commit()

    settings = get_settings()
    access_token_expires = timedelta(
        minutes=settings.access_token_expire_minutes
    )
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    response = RedirectResponse("http://localhost:8000/")

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # Allow http for now
        samesite="lax",
        expires=settings.access_token_expire_minutes * 60,
    )

    return response