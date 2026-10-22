# src/gitmind/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    github_token: str
    qdrant_url: str = "http://localhost:6333"
    groq_api_key: str
    qdrant_api_key: str | None = None
    database_url: str = "sqlite:///gitmind.db"

    model_config = SettingsConfigDict(env_file=".env")
    qdrant_collection: str = "gitmind_v2"
    allow_indexing: bool = True

settings = Settings()