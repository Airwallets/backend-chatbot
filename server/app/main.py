from typing import Annotated

from fastapi import FastAPI, Depends, status, HTTPException
from contextlib import asynccontextmanager

from .db.connection import get_sqlmodel_session
from .routers import user, chatbot, oauth, email, task

from .config import Settings, get_settings
from app.services.chatbot.checkpointer import initialise_checkpointer


# make global version of llm and graph in here (app.state)
@asynccontextmanager
async def lifespan(app: FastAPI):
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

app.include_router(chatbot.router)
app.include_router(oauth.router)
app.include_router(email.router)
app.include_router(task.router)


@app.get("/")
async def info(settings: Annotated[Settings, Depends(get_settings)]):
    return {"text": "Hello world", "test_host": settings.postgres_host}
