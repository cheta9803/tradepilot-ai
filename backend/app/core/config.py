from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TradePilot AI"
    app_version: str = "1.0.0"
    app_env: str = "development"

    host: str = "0.0.0.0"
    port: int = 8000

    database_url: str
    redis_url: str

    log_level: str = "INFO"

    secret_key: str

    access_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()