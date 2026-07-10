from datetime import datetime

from pydantic import BaseModel


class CandleResponse(BaseModel):
    exchange: str
    symbol: str
    token: str
    timeframe: str

    timestamp: datetime

    open: float
    high: float
    low: float
    close: float

    volume: int