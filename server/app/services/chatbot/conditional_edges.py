from app.services.chatbot.models import State

def routing_determine_user_intent(state: State) -> str:
    """
    Decide the next node based on the user intent
    """
    intent = state.get("intent")

    if intent == "generateInvoice":
        return "check_provided_invoice_details"
    elif intent == "sendEmail":
        return "check_provided_email_details"
    elif intent == "scheduleMeeting":
        return "check_provided_meeting_details"
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
    

def routing_check_provided_meeting_details(state: State) -> str:
    """
    Decide the next node based on the insertion details known
    """
    
    if (
        state.get("meeting_title") is None or
        state.get("recipient_email") is None or
        state.get("start_time") is None
    ):
        return "ask_for_meeting_details"
    else:
        return "schedule_meeting"
    

def routing_check_provided_email_details(state: State) -> str:
    """
    Decide the next node based on the email details known
    """
    
    if state.get("email_address") is None:
        return "ask_for_email_details"
    else:
        return "determine_email_satisfaction"
    

def routing_determine_email_satisfaction(state: State) -> str:
    """
    Decide the next node based on the user's generated email satisfaction
    """
    if state.get("satisfied") == "False":
        return "generate_email"
    else:
        return "send_email"


def routing_wait_for_user_input(state: State) -> str:
    """
    Decide the next node based on the user intent
    """

    if state.get("intent") is None:
        return "determine_user_intent"
    elif state.get("intent") == "generateInvoice":
        return "check_provided_invoice_details"
    elif state.get("intent") == "scheduleMeeting":
        return "check_provided_meeting_details"
    elif state.get("intent") == "sendEmail" and state.get("email_address") is None:
        return "check_provided_email_details"
    elif state.get("intent") == "sendEmail":
        return "determine_email_satisfaction"
    