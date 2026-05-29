import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # prioritizes environment variables
    MONGODB_URL: str = os.environ.get("MONGODB_URL", "mongodb://localhost:27017")
    DATABASE_NAME: str = "vaas_guard"

    REDIS_URL: str = os.environ.get("REDIS_URL", "redis://localhost:6379")

    LLM_PROVIDER: str = os.environ.get("LLM_PROVIDER", "openai")
    OPENAI_API_KEY: Optional[str] = os.environ.get("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.environ.get("ANTHROPIC_API_KEY")

    TARGET_URL: str = os.environ.get("TARGET_URL", "https://httpbin.org")
    PROXY_TIMEOUT: float = 5.0

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
