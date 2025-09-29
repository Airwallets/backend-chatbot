from typing import TypedDict, Annotated, List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

from langgraph.graph import add_messages

from app.schemas.app import User


# Define the state of the chatbot
class State(TypedDict):
    user: User
    messages: Annotated[list[str], add_messages]  # conversation history of all messages
    intent: Optional[str]  # user's current goal: generateInvoice, sendEmail, scheduleMeeting
    satisfied: Optional[str]
    
    # Email related atttributes
    email_address: Optional[str]
    email_subject: Optional[str]
    generated_email: Optional[str]

    # Invoice details
    name: str
    phone_number: str
    address: str
    item_name: str
    item_cost: float

    # Meeting details
    meeting_title: str
    recipient_email: str
    start_time: datetime


class UserIntent(BaseModel):
    """Classifies the user's intent based on their last message"""
    intent: Optional[Literal[
        "generateInvoice",
        "sendEmail",
        "scheduleMeeting"
    ]] = Field(
        default=None,
        description=(
            "The user's intent. Must be 'generateInvoice' if they want to create an invoice. "
            "Must be 'sendEmail' if they want to draft or send or reply to an email. "
            "Must be 'scheduleMeeting' if they want to arrange or book a meeting. "
            "Return null if none of these apply."
        )
    )


class InvoiceInfo(BaseModel):
    """Extracts the invoice details mentioned by the user"""
    name: Optional[str] = Field(default=None, description="The name of the person or company to whom the invoice is being sent")
    phone_number: Optional[str] = Field(default=None, description="The phone number of the person or company to whom the invoice is being sent")
    address: Optional[str] = Field(default=None, description="The address of the person or company to whom the invoice is being sent")
    item_name: Optional[str] = Field(default=None, description="The name of the item or service being invoiced")
    item_cost: Optional[float] = Field(default=None, description="The cost of the item or service")


class MeetingInfo(BaseModel):
    """Extracts the meeting details mentioned by the user"""
    meeting_title: Optional[str] = Field(default=None, description="The title or name of the meeting to be scheduled")
    recipient_email: Optional[str] = Field(default=None, description="The email address of the meeting recipient")
    start_time: Optional[datetime] = Field(
        default=None, 
        description="The meeting start time in ISO 8601 datetime format (e.g., 2025-09-29T15:30:00). "
                    "If the year is not specified, assume 2025. If the month is not specified, assume September (09)."
    )


class EmailSatisfaction(BaseModel):
    """Captures the user's satisfaction with a generated email."""
    satisfied: Literal["True", "False"] = Field(
        default="True",
        description=(
            "Indicates whether the user is satisfied with the generated email. "
            "Return 'True' if satisfied, 'False' if dissatisfied. Never return null."
        )
    )


class EmailInfo(BaseModel):
    """Extracts the email details mentioned by the user"""
    email_address: Optional[str] = Field(default=None, description="The email address of the email message recipient")