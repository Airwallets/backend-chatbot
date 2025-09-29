from functools import cache
from contextlib import asynccontextmanager

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.config import get_settings

@cache
def get_db_uri() -> str:
    """
    Returns the PostgreSQL connection string for LangGraph async checkpointer
    """
    settings = get_settings()
    return (
        f"postgresql://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:5432/{settings.postgres_db}?sslmode=disable"
    )

@asynccontextmanager
async def initialise_checkpointer():
    db_uri = get_db_uri()
    async with AsyncPostgresSaver.from_conn_string(db_uri) as checkpointer:
        await checkpointer.setup()
        yield checkpointer
