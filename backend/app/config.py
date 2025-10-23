from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENV: str = "dev"
    PORT: int = 8000
    DB_URL: str = "sqlite+aiosqlite:///./codeops.db"
    OPENAI_API_KEY: Optional[str] = None
    GITHUB_TOKEN: Optional[str] = None
    SLACK_WEBHOOK_URL: Optional[str] = None

    class Config:
        env_file = ".env"


settings = Settings()
