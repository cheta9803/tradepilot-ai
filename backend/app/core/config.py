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

    live_trading_enabled: bool = False

    market_close_hour: int = 15

    market_close_minute: int = 20

    trailing_stop_enabled: bool = True

    trailing_atr_multiplier: float = 1.0

    # Do not trail the position until it has moved meaningfully in our favor.
    # This avoids turning normal 1m/5m pullbacks into premature exits.
    trailing_start_atr_multiplier: float = 1.5

    breakeven_enabled: bool = True

    breakeven_atr_multiplier: float = 1.0

    max_open_trades: int = 5

    max_daily_loss: float = 2000.0

    cooldown_after_losses: int = 3

    cooldown_minutes: int = 30

    # After a losing trade, pause new entries for the same symbol.
    # This is intentionally shorter than the account-wide loss cooldown.
    symbol_loss_cooldown_minutes: int = 15

    # Entry-location filter. A BUY/SELL is rejected when the nearest
    # 5m/15m resistance/support leaves less room than the planned target
    # plus a small volatility buffer.
    entry_location_filter_enabled: bool = True
    entry_location_buffer_atr_multiplier: float = 0.25

    # -------------------------
    # Break-even Stop
    # -------------------------

    breakeven_enabled: bool = True

    breakeven_atr_multiplier: float = 1.0

    min_stop_move: float = 0.05

    # -------------------------------------------------

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()