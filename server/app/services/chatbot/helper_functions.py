from langchain_core.prompts import ChatPromptTemplate
from langgraph.types import interrupt

from app.services.chatbot.models import (
    UserIntent
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