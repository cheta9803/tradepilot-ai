from datetime import datetime

from pydantic import BaseModel

from app.domain.enums import TimeFrame


class Candle(BaseModel):
    symbol: str

    timeframe: TimeFrame

    timestamp: datetime

    open: float

    high: float

    low: float

    close: float

    volume: int