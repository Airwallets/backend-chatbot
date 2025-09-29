from datetime import timedelta
from fastapi import APIRouter
from typing import Annotated

from fastapi import Response, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.config import get_settings
from app.db.connection import SessionDep
from app.dependencies import get_current_user
from app.schemas.app import User
from app.models.api import UserResponse
import app.services.users as users
from app.services.auth import (
    Token,
    authenticate_user,
    create_access_token,
    UserSignup,
    signup_user,
    UserLogin,
)

router = APIRouter(tags=["users"])


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
) -> Token:
    """
    Retrieves the access token given login details in *form_data*
    """
    user = authenticate_user(
        session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    settings = get_settings()
    access_token_expires = timedelta(
        minutes=settings.access_token_expire_minutes
    )
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="Bearer")


@router.post("/users/login")
async def user_login(user: UserLogin, session: SessionDep, response: Response):
    user = authenticate_user(session, email=user.email, password=user.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    settings = get_settings()
    access_token_expires = timedelta(
        minutes=settings.access_token_expire_minutes
    )
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # Allow http for now
        samesite="lax",
        expires=settings.access_token_expire_minutes * 60,
    )

    return {"message": "Logged in"}


@router.post("/users/logout")
async def user_logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logged out"}


@router.post("/users/signup")
def signup(signup: UserSignup, session: SessionDep, response: Response):
    """
    Create a new user given details in *signup*
    """
    if users.find_one(session, signup.email) is not None:
        response.status_code = status.HTTP_409_CONFLICT
        return {"message": "Username already taken"}

    signup_user(session, signup)

    return {"message": "success"}


@router.get("/users/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    """
    Retrieves the currently logged in user
    """
    return current_user
