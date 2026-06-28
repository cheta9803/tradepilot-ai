from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CandleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    symbol: str
    timeframe: str
    timestamp: datetime

    open: float
    high: float
    low: float
    close: float

    volume: int