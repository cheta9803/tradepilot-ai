from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # -------------------------------------------------
    # Application
    # -------------------------------------------------

    app_name: str = "TradePilot AI"
    app_version: str = "1.0.0"
    app_env: str = "development"

    host: str = "0.0.0.0"
    port: int = 8000

    log_level: str = "INFO"

    # -------------------------------------------------
    # Database
    # -------------------------------------------------

    database_url: str
    redis_url: str

    # -------------------------------------------------
    # Security
    # -------------------------------------------------

    secret_key: str
    access_token_expire_minutes: int = 60

    # -------------------------------------------------
    # Angel One SmartAPI
    # -------------------------------------------------

    angel_api_key: str = ""
    angel_client_id: str = ""
    angel_pin: str = ""
    angel_totp_secret: str = ""

    # -------------------------------------------------
    # Trading Configuration
    # -------------------------------------------------

    default_capital: float = 100000.0

    risk_percent: float = 1.0

    paper_trading: bool = True

    market_close_hour: int = 15

    market_close_minute: int = 20

    # -------------------------------------------------

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()