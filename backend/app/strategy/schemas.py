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

    ema20: float
    rsi14: float
    atr14: float
    vwap: float
    macd: float
    signal_line: float

    reasons: list[str]