from pydantic import BaseModel


class PaperTradeRequest(BaseModel):
    exchange: str
    token: str
    timeframe: str = "1m"