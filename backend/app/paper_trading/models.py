from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class PaperTrade:
    id: Optional[int]

    symbol: str

    side: str

    quantity: int

    entry_price: float

    exit_price: Optional[float]

    stop_loss: float

    target: float

    status: str

    pnl: float

    opened_at: datetime

    closed_at: Optional[datetime]