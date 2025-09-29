import jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlmodel import select

from app.config import get_settings
from app.db.connection import SessionDep
from app.schemas.app import User, UserDetails
import app.services.users as users


class Token(BaseModel):
    access_token: str
    token_type: str


class UserSignup(UserDetails):
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


pwd_context = CryptContext()
pwd_context.load_path("app/policy.ini")


def verify_password(plain: str, hashed: str):
    """
    Verify the plain_password matches the hashed_password after hashed
    """
    return pwd_context.verify(plain, hashed, scheme="argon2")


def get_password_hash(password: str):
    """
    Hash the password following bcrypt schemes
    """
    return pwd_context.hash(password, scheme="argon2")


def signup_user(session: SessionDep, signup: UserSignup) -> User:
    """
    Add a new user into the database
    """
    user = User(
        saltpassword=get_password_hash(signup.password),
        email=signup.email,
        name=signup.name,
    )

    users.add_one(session, user)
    return user


def authenticate_user(
    session: SessionDep, email: str, password: str
) -> User | None:
    """
    Finds the user given the email and password. Returns None if invalid credentials
    """
    user = users.find_one(session, email)
    if user is None:
        return None

    if not verify_password(plain=password, hashed=user.saltpassword):
        return None

    return user


def create_access_token(data: dict, expires_delta: timedelta) -> str:
    """
    Create a jwt access token, encoding `data`, expired after `expires_delta`.
    """
    settings = get_settings()
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt
