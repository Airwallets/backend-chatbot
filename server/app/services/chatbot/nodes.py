from langchain.schema import AIMessage, HumanMessage

from app.services.chatbot.helper_functions import (
    extract_user_intent
)
from app.services.chatbot.models import State


async def determine_user_intent_node(model, state: State):
    """
    Node to extract the user intent from the user's message
    """
    last_message = state.get("messages")[-1].content if state.get("messages") else ""
    intent = extract_user_intent(model, last_message)

    return {"intent": intent}


async def prompt_for_correct_user_intent_node(model, state: State):
    """
    Node to inform the user of its actions
    """
   
    prompt = (
        "You are a helpful assistant that guides users about supported actions. "
        "You can only support five actions:\n"
        "1. Generating an invoice (generateInvoice).\n"
        "2. Parsing or extracting details from an invoice (parseInvoice).\n"
        "3. Drafting or sending an email (sendEmail).\n"
        "4. Replying to an email (replyEmail).\n"
        "5. Scheduling or arranging a meeting (scheduleMeeting).\n\n"
        "If the user requests something else, politely explain that you cannot help with that and "
        "redirect them to one of the five supported actions.\n\n"
        "Conversation so far:\n"
        f"{state.get('messages')}\n\n"
        "Now, respond politely to the user."
    )

    response = await model.ainvoke(prompt)
    return {
        "messages": [response]
    }