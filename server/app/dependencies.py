import jwt
from typing import Annotated
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer

from app.db.connection import SessionDep
from app.config import get_settings
from app.schemas.app import User
import app.services.users as users

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_token_cookie_or_oauth2(request: Request):
    # Try cookies
    token = request.cookies.get("access_token")

    # If not cookies, then try oauth2
    # Automatic throw HttpException if not oauth2
    if not token:
        token = await oauth2_scheme(request)

    return token


async def get_current_user(
    token: Annotated[str, Depends(get_token_cookie_or_oauth2)],
    session: SessionDep,
) -> User:
    """
    Use as dependency for any api endpoint that require authentication.
    Will return the user's db record if exist, else throws.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        settings = get_settings()
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        email = payload.get("sub")
        if email is None:
            raise credentials_exception

    except InvalidTokenError:
        # Auto throw if the token expired
        raise credentials_exception

    user = users.find_one(session, email)
    if user is None:
        raise credentials_exception

    return user
