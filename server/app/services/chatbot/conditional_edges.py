from app.services.chatbot.models import State

def routing_determine_user_intent(state: State) -> str:
    """
    Decide the next node based on the user intent
    """
    intent = state.get("intent")

    if intent == "generateInvoice":
        return "generate_invoice"
    elif intent == "parseInvoice":
        return "parse_invoice"
    elif intent == "sendEmail":
        return "send_email"
    elif intent == "replyEmail":
        return "reply_email"
    elif intent == "scheduleMeeting":
        return "schedule_meeting"
    else:
        return "prompt_for_correct_user_intent"