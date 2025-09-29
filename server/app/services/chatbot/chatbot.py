import os
from functools import cache

from langchain.chat_models import init_chat_model

from app.config import get_settings


@cache
def get_chatbot():
    # Initialise chat model with Mistral AI
    os.environ["MISTRAL_API_KEY"] = get_settings().mistral_api_key

    # Initialise LLM
    return init_chat_model("mistral-small-latest", model_provider="mistralai")
