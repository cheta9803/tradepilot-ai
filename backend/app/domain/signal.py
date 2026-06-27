from pydantic import BaseModel

from app.domain.enums import SignalType


class TradeSignal(BaseModel):
    symbol: str

    signal: SignalType

    entry: float

    stop_loss: float

    target: float

    confidence: float

    reason: str