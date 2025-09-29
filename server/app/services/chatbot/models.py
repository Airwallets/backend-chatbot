from typing import TypedDict, Annotated, List, Optional, Literal
from pydantic import BaseModel, Field

from langgraph.graph import add_messages


# Define the state of the chatbot
class State(TypedDict):
    messages: Annotated[list[str], add_messages]  # conversation history of all messages
    intent: Optional[str]  # user's current goal: generateInvoice, parseInvoice, sendEmail, replyEmail, scheduleMeeting
    

class UserIntent(BaseModel):
    """Classifies the user's intent based on their last message"""
    intent: Optional[Literal[
        "generateInvoice",
        "parseInvoice",
        "sendEmail",
        "replyEmail",
        "scheduleMeeting"
    ]] = Field(
        default=None,
        description=(
            "The user's intent. Must be 'generateInvoice' if they want to create an invoice. "
            "Must be 'parseInvoice' if they want to extract or analyse information from an invoice. "
            "Must be 'sendEmail' if they want to draft or send an email. "
            "Must be 'replyEmail' if they want to respond to an existing email. "
            "Must be 'scheduleMeeting' if they want to arrange or book a meeting. "
            "Return null if none of these apply."
        )
    )