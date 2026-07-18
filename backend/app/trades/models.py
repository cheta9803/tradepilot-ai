from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Trade:

    exchange: str
    token: str
    symbol: str

    timeframe: str

    state: str

    signal: str

    entry_price: float
    stop_loss: float
    target: float

    quantity: int

    opened_at: datetime | None = None
    closed_at: datetime | None = None

    exit_price: float | None = None

    pnl: float = 0.0

    reason: str | None = None