from pydantic import BaseModel


class EMAResponse(BaseModel):
    symbol: str
    timeframe: str
    period: int
    ema: float