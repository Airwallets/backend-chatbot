from uuid import uuid4, UUID
from typing import Optional, Any
from datetime import datetime
from enum import Enum
from sqlmodel import Field, SQLModel, Relationship
from pgvector.sqlalchemy import Vector


# -----------------------------
# APPLICATION TABLES
# -----------------------------

class UserDetails(SQLModel):
    email: str = Field()
    name: str = Field()


class User(UserDetails, table=True):
    __tablename__ = "app_user"

    user_id: UUID = Field(default_factory=uuid4, primary_key=True)
    saltpassword: str = Field()
    created_at: datetime = Field(default_factory=datetime.now)
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None

    # Relationships
    knowledges: list["Knowledge"] = Relationship(back_populates="creator")
    invoices: list["Invoice"] = Relationship(back_populates="creator")
    emails: list["Email"] = Relationship(back_populates="user")

    

class Knowledge(SQLModel, table=True):
    __tablename__ = "knowledge"

    knowledge_id: UUID = Field(default_factory=uuid4, primary_key=True)
    creator_id: UUID = Field(foreign_key="app_user.user_id")
    title: str = Field(nullable=False)
    body: str = Field(nullable=False)
    embedding: Any = Field(sa_type=Vector(1024))

    # Relationship back to user
    creator: Optional[User] = Relationship(back_populates="knowledges")

class BaseEmail(SQLModel):
    from_sender: Optional[str] = None
    email_subject: Optional[str] = None
    email_status: Optional[str] = None
    email_timestamp: Optional[datetime] = None
    full_content: Optional[str] = None
    summary: Optional[str] = None
    draft_response: Optional[str] = None

class Email(BaseEmail, table=True):
    __tablename__ = "email"
    email_id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="app_user.user_id")

    user: Optional[User] = Relationship(back_populates="emails")
    tasks: list["Task"] = Relationship(back_populates="email")

class Task(SQLModel, table=True):
    __tablename__ = "task"

    task_id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: Optional[str] = None
    task_description: Optional[str] = None
    task_priority: Optional[str] = None
    due_date: Optional[datetime] = None
    completed: Optional[str] = None
    email_id: Optional[UUID] = Field(default=None, foreign_key="email.email_id")
    created_at: datetime = Field(default_factory=datetime.now)

    email: Optional[Email] = Relationship(back_populates="tasks")

class Invoice(SQLModel, table=True):
    __tablename__ = "invoice"

    invoice_id: UUID = Field(default_factory=uuid4, primary_key=True)
    creator_id: UUID = Field(foreign_key="app_user.user_id")
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    consumer_address: Optional[str] = None
    item_name: Optional[str] = None
    item_cost: Optional[float] = None

    creator: Optional[User] = Relationship(back_populates="invoices")