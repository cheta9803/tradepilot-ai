from pydantic import BaseModel


class BroadcastTickRequest(BaseModel):

    exchange: str = "NSE"

    symbol: str

    trading_symbol: str

    token: str

    ltp: float

    open: float = 0.0

    high: float = 0.0

    low: float = 0.0

    close: float = 0.0

    volume: int = 0

    timestamp: str