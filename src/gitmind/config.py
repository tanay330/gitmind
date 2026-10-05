# src/gitmind/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    github_token: str
    qdrant_url: str = "http://localhost:6333"
    groq_api_key: str
    qdrant_api_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()