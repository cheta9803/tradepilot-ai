from pydantic import BaseModel


class EMAResponse(BaseModel):
    symbol: str
    timeframe: str
    period: int
    ema: float


class SMAResponse(BaseModel):
    symbol: str
    timeframe: str
    period: int
    sma: float


class RSIResponse(BaseModel):
    symbol: str
    timeframe: str
    period: int
    rsi: float