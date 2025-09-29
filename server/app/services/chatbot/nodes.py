from langchain.schema import AIMessage, HumanMessage

from app.services.chatbot.helper_functions import (
    user_input, 
    extract_user_intent, 
)
from app.services.chatbot.models import State


async def determine_user_intent_node(model, state: State):
    """
    Node to extract the user intent from the user's message
    """
    last_message = state.get("messages")[-1].content if state.get("messages") else ""
    intent = extract_user_intent(model, last_message)

    return {"intent": intent}