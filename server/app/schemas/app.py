import uuid
from typing import Optional, Any
from datetime import datetime
from enum import Enum
from sqlmodel import Field, SQLModel, Relationship
from pgvector.sqlalchemy import Vector



# -----------------------------
# APPLICATION TABLES
# -----------------------------



class UserStatus(str, Enum):
    OK = "ok"
    RESTRICTED = "restricted"
    BANNED = "banned"


class UserDetails(SQLModel):
    email: str = Field()
    name: Optional[str] = Field(None, nullable=True)
    region: Optional[str] = Field(None, nullable=True)
    location: Optional[str] = Field(None, nullable=True)


class User(UserDetails, table=True):
    __tablename__ = "app_user"

    user_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    saltpassword: str = Field()
    status: UserStatus = Field(default=UserStatus.OK)
    created_at: datetime = Field(default_factory=datetime.now)
