from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import os


class Settings(BaseSettings):
    mode: str
    postgres_password: str = os.getenv("POSTGRES_PASSWORD")
    postgres_host: str = os.getenv("POSTGRES_HOST")
    postgres_user: str = os.getenv("POSTGRES_USER")
    postgres_db: str = os.getenv("POSTGRES_DB")
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    mistral_api_key: str
    hf_token: str  # required for tokenizer to work

    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str

    model_config = SettingsConfigDict(
        env_file=(
            "app/.env" if os.getenv("MODE", "") == "PROD" else "app/.env.test"
        )
    )


@lru_cache
def get_settings() -> Settings:
    """
    Global endpoint to obtain the environment variables.
    Call get_settings (or used as dependencies) to obtain the env variables.
    Use cache to avoid reading the .env multiple times.
    """
    return Settings()
