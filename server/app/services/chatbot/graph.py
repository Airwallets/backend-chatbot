from functools import partial

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.services.chatbot.chatbot import get_chatbot
from app.services.chatbot.nodes import (
    determine_user_intent_node,
    prompt_for_correct_user_intent_node
)
from app.services.chatbot.conditional_edges import (
    routing_determine_user_intent
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

    # Add edges to the graph
    graph_builder.add_edge(START, "determine_user_intent")

    # Add conditional edges to the graph
    graph_builder.add_conditional_edges("determine_user_intent", routing_determine_user_intent)

    return graph_builder.compile(checkpointer=checkpointer, debug=True)
