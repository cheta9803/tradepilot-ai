from pydantic import BaseModel


class LivePriceResponse(BaseModel):
    exchange: str
    symbol: str
    token: str

    ltp: float

    open: float
    high: float
    low: float
    close: float

    volume: int

    timestamp: str