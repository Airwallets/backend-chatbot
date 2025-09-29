from langchain.schema import AIMessage, HumanMessage

from app.services.chatbot.helper_functions import (
    extract_user_intent,
    extract_invoice_info,
    extract_meeting_info,
    extract_email_satisfaction,
    user_input
)
from app.services.chatbot.models import State

from app.services.google import create_google_api_client, create_calendar_event


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


async def wait_for_user_input_node(model, state: State):
    """
    Node to request user input
    """ 
    
    user_reply_text = user_input(state.get("messages")[-1].content)
    user_reply = HumanMessage(content=user_reply_text)
    return {
        "messages": [user_reply]
    }


async def check_provided_invoice_details_node(model, state: State):
    """
    Node to check if any invoice details are provided, if not tries to extract it from the last user message
    """
    
    # Extract provided service details from the last user message
    last_message = state.get("messages")[-1].content if state.get("messages") else ""
    extracted_info = extract_invoice_info(model, last_message)
    
    return {
        "name": extracted_info.get("name"),
        "phone_number": extracted_info.get("phone_number"),
        "address": extracted_info.get("address"),
        "item_name": extracted_info.get("item_name"),
        "item_cost": extracted_info.get("item_cost")
    }


async def ask_for_invoice_details_node(model, state: State):
    """
    Node to check which invoice details are missing and ask the user for them
    """
    
    required_details = ["name", "phone_number", "address", "item_name", "item_cost"]
    
    # Find which details are still missing
    missing_details = [detail for detail in required_details if not state.get(detail)]
    
    # Construct a prompt asking for the missing details
    if len(missing_details) == 1:
        prompt_text = (
            f"I am happy to help you generate an invoice. "
            f"Could you please provide the {missing_details[0]} for the invoice?"
        )
    
    else:
        # Join the details into a readable phrase to ask the user
        fields_phrase = ", ".join(missing_details[:-1]) + f" and {missing_details[-1]}"
        prompt_text = (
            f"I am happy to help you generate an invoice. "
            f"Could you please provide the {fields_phrase} for the invoice?"
        )

    return {
        "messages": [AIMessage(content=prompt_text)]
    }


async def generate_invoice_node(model, state: State):
    """
    Node to generate an invoice
    """
    name = state.get("name")
    phone_number = state.get("phone_number")
    address = state.get("address")
    item_name = state.get("item_name")
    cost = state.get("item_cost")

    invoice = (
        "=== Invoice ===\n"
        f"Name: {name}\n"
        f"Phone: {phone_number}\n"
        f"Address: {address}\n\n"
        f"Item: {item_name}\n"
        f"Cost: ${cost:.2f}\n"
        "================"
    )

    return {
        "invoice": invoice,
        "messages": [AIMessage(content=f"Generated invoice:\n{invoice}")]
    }


async def check_provided_meeting_details_node(model, state: State):
    """
    Node to check if any meeting details are provided, if not tries to extract it from the last user message
    """
    
    # Extract provided meeting details from the last user message
    last_message = state.get("messages")[-1].content if state.get("messages") else ""
    extracted_info = extract_meeting_info(model, last_message)
    
    return {
        "meeting_title": extracted_info.get("meeting_title"),
        "recipient_email": extracted_info.get("recipient_email"),
        "start_time": extracted_info.get("start_time")
    }


async def ask_for_meeting_details_node(model, state: State):
    """
    Node to check which meeting details are missing and ask the user for them
    """
    
    required_details = ["meeting_title", "recipient_email", "start_time"]
    
    # Find which details are still missing
    missing_details = [detail for detail in required_details if not state.get(detail)]
    
    # Construct a prompt asking for the missing details
    if len(missing_details) == 1:
        prompt_text = (
            f"I am happy to help you schedule a meeting. "
            f"Could you please provide the {missing_details[0]} for the meeting?"
        )
    
    else:
        # Join the details into a readable phrase to ask the user
        fields_phrase = ", ".join(missing_details[:-1]) + f" and {missing_details[-1]}"
        prompt_text = (
            f"I am happy to help you schedule a meeting. "
            f"Could you please provide the {fields_phrase} for the meeting?"
        )

    return {
        "messages": [AIMessage(content=prompt_text)]
    }


async def schedule_meeting_node(model, state: State):
    """
    Node to schedule a meeting
    """
    meeting_title = state.get("meeting_title")
    recipient_email = state.get("recipient_email")
    start_time = state.get("start_time")
    user = state.get("user")

    calendar_client = create_google_api_client("calendar", user)

    create_calendar_event(
        client=calendar_client,
        title=meeting_title,
        email=recipient_email,
        start_time=start_time
    )

    start_time_str = start_time.strftime("%Y-%m-%d %H:%M")

    return {
        "messages": [AIMessage(content=f"Scheduled meeting with {recipient_email} at {start_time_str}")]
    }


async def generate_email_node(model, state: State):
    """
    Node to generate an email
    """

    email_sender = state.get("user").name

    prompt = (
        f"You are an AI assistant tasked with drafting a professional, polite work email.\n"
        f"The sender of the email should be: {email_sender}\n\n"
        f"Conversation context:\n{state.get('messages')}\n\n"
        "Compose the email clearly, concisely, and appropriately for a professional setting."
    )

    response = await model.ainvoke(prompt)
    return {
        "messages": [AIMessage(content=f"Here's an email I generated:\n\n{response.content}. Would you like me to send it?")],
        "generated_email": response
    }


async def determine_email_satisfaction_node(model, state: State):
    """
    Node to extract satisfaction about the generated email
    """
    last_message = state.get("messages")[-1].content if state.get("messages") else ""
    satisfied = extract_email_satisfaction(model, last_message)

    return {"satisfied": satisfied}