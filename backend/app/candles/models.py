from dataclasses import dataclass
from datetime import datetime


@dataclass
class Candle:

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