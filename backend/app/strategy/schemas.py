from pydantic import BaseModel


class StrategyResponse(BaseModel):
    symbol: str
    timeframe: str

    signal: str
    confidence: int

    entry: float
    stop_loss: float
    target: float

    risk_reward: float

    reasons: list[str]