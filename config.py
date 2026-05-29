from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    # MongoDB URL from env or default to local (though Render will provide it)
    MONGODB_URL: Optional[str] = os.environ.get("MONGODB_URL", "mongodb://localhost:27017")
    DATABASE_NAME: str = "vaas_guard"

    # Redis URL from env or default to local
    REDIS_URL: Optional[str] = os.environ.get("REDIS_URL", "redis://localhost:6379")

    # LLM Settings
    LLM_PROVIDER: str = "openai"  # "openai" or "anthropic"
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    TARGET_URL: str = "https://httpbin.org"
    PROXY_TIMEOUT: float = 5.0

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
