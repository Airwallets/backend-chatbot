from functools import partial

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.services.chatbot.chatbot import get_chatbot
from app.services.chatbot.nodes import (
    determine_user_intent_node,
    prompt_for_correct_user_intent_node,
    wait_for_user_input_node,
    check_provided_invoice_details_node,
    ask_for_invoice_details_node,
    generate_invoice_node,
    check_provided_meeting_details_node,
    ask_for_meeting_details_node,
    schedule_meeting_node,
    generate_email_node,
    determine_email_satisfaction_node,
    send_email_node,
    check_provided_email_details_node,
    ask_for_email_details_node

)
from app.services.chatbot.conditional_edges import (
    routing_determine_user_intent,
    routing_check_provided_invoice_details,
    routing_check_provided_meeting_details,
    routing_check_provided_email_details,
    routing_determine_email_satisfaction,
    routing_wait_for_user_input
)
from app.services.chatbot.models import State


async def get_graph(checkpointer: AsyncPostgresSaver = None) -> StateGraph:
    """
    Create the langgraph graph for a session
    """
    model = get_chatbot()

    # Build the graph
    graph_builder = StateGraph(State)

    # Add nodes to the graph
    graph_builder.add_node("determine_user_intent", partial(determine_user_intent_node, model))
    graph_builder.add_node("prompt_for_correct_user_intent", partial(prompt_for_correct_user_intent_node, model))
    graph_builder.add_node("wait_for_user_input", partial(wait_for_user_input_node, model))
    graph_builder.add_node("check_provided_invoice_details", partial(check_provided_invoice_details_node, model))
    graph_builder.add_node("ask_for_invoice_details", partial(ask_for_invoice_details_node, model))
    graph_builder.add_node("generate_invoice", partial(generate_invoice_node, model))
    graph_builder.add_node("check_provided_meeting_details", partial(check_provided_meeting_details_node, model))
    graph_builder.add_node("ask_for_meeting_details", partial(ask_for_meeting_details_node, model))
    graph_builder.add_node("schedule_meeting", partial(schedule_meeting_node, model))
    graph_builder.add_node("generate_email", partial(generate_email_node, model))
    graph_builder.add_node("determine_email_satisfaction", partial(determine_email_satisfaction_node, model))
    graph_builder.add_node("send_email", partial(send_email_node, model))
    graph_builder.add_node("check_provided_email_details", partial(check_provided_email_details_node, model))
    graph_builder.add_node("ask_for_email_details", partial(ask_for_email_details_node, model))

    # Add edges to the graph
    graph_builder.add_edge(START, "determine_user_intent")
    graph_builder.add_edge("prompt_for_correct_user_intent", "wait_for_user_input")
    graph_builder.add_edge("ask_for_invoice_details", "wait_for_user_input")
    graph_builder.add_edge("ask_for_meeting_details", "wait_for_user_input")
    graph_builder.add_edge("ask_for_email_details", "wait_for_user_input")
    graph_builder.add_edge("generate_email", "wait_for_user_input")
    graph_builder.add_edge("check_provided_email_details", "generate_email")
    graph_builder.add_edge("generate_invoice", END)
    graph_builder.add_edge("schedule_meeting", END)
    graph_builder.add_edge("send_email", END)

    # Add conditional edges to the graph
    graph_builder.add_conditional_edges("determine_user_intent", routing_determine_user_intent)
    graph_builder.add_conditional_edges("check_provided_invoice_details", routing_check_provided_invoice_details)
    graph_builder.add_conditional_edges("check_provided_meeting_details", routing_check_provided_meeting_details)
    graph_builder.add_conditional_edges("check_provided_email_details", routing_check_provided_email_details)
    graph_builder.add_conditional_edges("determine_email_satisfaction", routing_determine_email_satisfaction)
    graph_builder.add_conditional_edges("wait_for_user_input", routing_wait_for_user_input)

    return graph_builder.compile(checkpointer=checkpointer, debug=True)
