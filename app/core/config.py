from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="APP_",
        extra="ignore",
    )

    name: str = "AI Engineering Platform"
    version: str = "0.1.0"
    environment: str = "development"
    log_level: str = "INFO"

    database_url: str = (
        "postgresql+psycopg://app_user:"
        "local_dev_password_change_me@localhost:5433/"
        "ai_engineering_platform"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
