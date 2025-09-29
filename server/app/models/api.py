# Schema for api endpoints response (or anything api specific, and not db).
# Avoid using the same schema as the db to avoid leaking secrets (eg: password).
from enum import Enum

from pydantic import BaseModel
from typing import Optional
from app.schemas.app import ApprovedStatus, UserDetails
from app.schemas.service import *
import uuid
from datetime import datetime


class UserResponse(BaseModel):
    """
    Used in replacement of User db schema when return via api.
    To avoid leaking sensitive info (eg: salt password).
    """

    email: str
    name: Optional[str]
    region: Optional[str]
    location: Optional[str]
    type: Optional[str] | None = None

