from pydantic import BaseModel


class StrategyResponse(BaseModel):

    exchange: str

    token: str

    symbol: str

    timeframe: str

    trend: str

    signal: str

    confidence: int

    tradable: bool

    entry: float

    stop_loss: float

    target: float

    risk_reward: float

    ema20: float

    ema50: float

    rsi14: float

    atr14: float

    vwap: float | None

    macd: float

    signal_line: float

    reasons: list[str]