from fastapi import APIRouter, Request, Depends
from pydantic import BaseModel
from typing import Optional

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.types import Command

from app.services.chatbot.graph import get_graph
from app.schemas.app import User
from app.dependencies import get_current_user


router = APIRouter()


class ChatbotQuery(BaseModel):
    message: str
    thread_id: str
    resume: Optional[bool] = False


@router.post("/chatbot/query")
async def chatbot_query(
    request: Request, 
    query: ChatbotQuery,
    current_user: User = Depends(get_current_user)
):
    """
    Processes a user's message with the chatbot and returns the chatbot's reply.
    """
    
    # Initialise the checkpointer and the chatbot state graph
    checkpointer: AsyncPostgresSaver = request.app.state.checkpointer
    graph = await get_graph(checkpointer=checkpointer)

    config = {"configurable": {"thread_id": query.thread_id}}

    # Initialise the state of the graph with the current user & the next user message
    state_dict = {
        "user": current_user,
        "messages": [{"role": "user", "content": query.message}]
    }

    # User is responding to a message from the chatbot
    if query.resume == True:
        response = await graph.ainvoke(
            Command(resume={"data": query.message}), 
            config
        )
    else:
        # User is beginning a conversation with the chatbot
        response = await graph.ainvoke(
            state_dict,
            config
        )

    # Otherwise return bot’s latest message
    return response["messages"][-1].content