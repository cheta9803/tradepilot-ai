from pydantic import BaseModel


class WatchlistLiveResponse(BaseModel):
    id: int

    exchange: str
    symbol: str

    token: str
    trading_symbol: str

    ltp: float | None = None
    change: float | None = None
    change_percent: float | None = None

    open: float | None = None
    high: float | None = None
    low: float | None = None
    close: float | None = None

    volume: int | None = None

    timestamp: str | None = None