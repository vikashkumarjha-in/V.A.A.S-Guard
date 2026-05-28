from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    MONGODB_URL: str = "mongodb://mongodb:27017"
    DATABASE_NAME: str = "vaas_guard"
    REDIS_URL: str = "redis://redis:6379"

    # LLM Settings
    LLM_PROVIDER: str = "openai"  # "openai" or "anthropic"
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    TARGET_URL: str = "https://httpbin.org"
    PROXY_TIMEOUT: float = 5.0

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
