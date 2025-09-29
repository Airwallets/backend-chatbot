from langchain_core.prompts import ChatPromptTemplate
from langgraph.types import interrupt

from app.services.chatbot.models import (
    UserIntent,
    InvoiceInfo
)


# Prompt template for intent extraction
intent_prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system",
            "You are an expert at classifying a user's intent when they provide instructions. "
            "Classify the intent strictly as one of the following: "
            "'generateInvoice' if the user wants to create or generate an invoice. "
            "'parseInvoice' if the user wants to extract or read information from an invoice. "
            "'sendEmail' if the user wants to draft or send an email. "
            "'replyEmail' if the user wants to respond to an email they received. "
            "'scheduleMeeting' if the user wants to arrange, book, or plan a meeting. "
            "Return null if the user's intent does not match any of these five categories."),
        ("human", "{text}"),
    ]
)


# Prompt template for extracting invoice information from the user's message for insertion
invoice_extraction_prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", 
            "You are an expert at extracting invoice information from a user's message."
            "Extract the following fields if available: "
            "- name: the recipient's name"
            "- phone_number: the recipient's phone number"
            "- address: the recipient's address"
            "- item_name: the item or service being invoiced"
            "- item_cost: the cost of the item or service"
        ),
        ("human", "{text}"),
    ]
)

def extract_user_intent(model, user_message: str) -> str:
    """
    Uses the structured LLM to classify the user's intent from the user's message.
    Returns 'searchService', 'addService', or None.
    """
    # Build prompt
    prompt = intent_prompt_template.invoke({"text": user_message})

    # Structured output
    structured_llm = model.with_structured_output(schema=UserIntent)
    result = structured_llm.invoke(prompt)

    return result.intent


def extract_invoice_info(model, user_message: str) -> dict:
    """
    Uses the structured LLM to extract name, phone number, address, item name and item cost from the user's message.
    Returns dict with optional 'name', 'phone number', 'address', 'item name' and 'item cost' fields
    """
    # Build prompt
    prompt = invoice_extraction_prompt_template.invoke({"text": user_message})
    
    # Structured output
    structured_llm = model.with_structured_output(schema=InvoiceInfo)
    result = structured_llm.invoke(prompt)

    return {
        "name": result.name,
        "phone_number": result.phone_number,
        "address": result.address,
        "item_name": result.item_name,
        "item_cost": result.item_cost
    }


def user_input(query: str) -> str: 
    """
    Request user input
    """ 
    user_response = interrupt({"query": query}) 
    return user_response["data"]