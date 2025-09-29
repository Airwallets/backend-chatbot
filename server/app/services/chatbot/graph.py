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
    schedule_meeting_node

)
from app.services.chatbot.conditional_edges import (
    routing_determine_user_intent,
    routing_check_provided_invoice_details
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
    graph_builder.add_node("schedule_meeting", partial(schedule_meeting_node, model))

    # Add edges to the graph
    graph_builder.add_edge(START, "determine_user_intent")
    graph_builder.add_edge("ask_for_invoice_details", "wait_for_user_input")

    # Add conditional edges to the graph
    graph_builder.add_conditional_edges("determine_user_intent", routing_determine_user_intent)
    graph_builder.add_conditional_edges("check_provided_invoice_details", routing_check_provided_invoice_details)

    return graph_builder.compile(checkpointer=checkpointer, debug=True)
