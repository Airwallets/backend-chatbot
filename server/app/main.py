from typing import Annotated

from fastapi import FastAPI, Depends, status, HTTPException
from contextlib import asynccontextmanager

from .db.connection import get_sqlmodel_session
from .routers import user, service, chatbot, conversation
from .config import Settings, get_settings
from .services.users import init_roles
from app.services.chatbot.checkpointer import initialise_checkpointer


# make global version of llm and graph in here (app.state)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # TODO: Review and move this to the db side, not the server
    session = next(get_sqlmodel_session())
    init_roles(session)

    # Initialise the checkpointer and store it in app state
    async with initialise_checkpointer() as cp:
        app.state.checkpointer = cp
        yield


app = FastAPI(
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "users",
            "description": "Operations with users, including authentication",
        }
    ],
)
app.include_router(user.router)


@app.get("/")
async def info(settings: Annotated[Settings, Depends(get_settings)]):
    return {"text": "Hello world", "test_host": settings.postgres_host}
