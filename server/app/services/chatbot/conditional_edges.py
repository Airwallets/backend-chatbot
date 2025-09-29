from app.services.chatbot.models import State

def routing_determine_user_intent(state: State) -> str:
    """
    Decide the next node based on the user intent
    """
    intent = state.get("intent")

    if intent == "generateInvoice":
        return "check_provided_invoice_details"
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
    

def routing_check_provided_invoice_details(state: State) -> str:
    """
    Decide the next node based on the insertion details known
    """
    
    if (
        state.get("name") is None or
        state.get("phone_number") is None or
        state.get("address") is None or
        state.get("item_name") is None or
        state.get("item_cost") is None
    ):
        return "ask_for_invoice_details"
    else:
        return "generate_invoice"
    

def routing_wait_for_user_input(state: State) -> str:
    """
    Decide the next node based on the user intent
    """

    if state.get("intent") is None:
        return "determine_user_intent"
    elif state.get("intent") == "generateInvoice":
        return "check_provided_invoice_details"
    