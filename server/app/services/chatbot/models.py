from typing import TypedDict, Annotated, List, Optional, Literal
from pydantic import BaseModel, Field

from langgraph.graph import add_messages


# Define the state of the chatbot
class State(TypedDict):
    messages: Annotated[list[str], add_messages]  # conversation history of all messages
    intent: Optional[str]  # user's current goal: generateInvoice, parseInvoice, sendEmail, replyEmail, scheduleMeeting

    # Invoice details
    name: str
    phone_number: str
    address: str
    item_name: str
    item_cost: float
    

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


class InvoiceInfo(BaseModel):
    """Extracts the invoice details mentioned by the user"""
    name: Optional[str] = Field(default=None, description="The name of the person or company to whom the invoice is being sent")
    phone_number: Optional[str] = Field(default=None, description="The phone number of the person or company to whom the invoice is being sent")
    address: Optional[str] = Field(default=None, description="The address of the person or company to whom the invoice is being sent")
    item_name: Optional[str] = Field(default=None, description="The name of the item or service being invoiced")
    item_cost: Optional[float] = Field(default=None, description="The cost of the item or service")
