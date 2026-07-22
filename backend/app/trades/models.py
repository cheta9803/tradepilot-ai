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

    opened_at: str | None = None

    closed_at: str | None = None

    exit_price: float | None = None

    pnl: float = 0.0

    # NEW
    current_price: float = 0.0

    reason: str | None = None

    updated_at: str = datetime.now().isoformat()

    # -------------------------
    # Risk State
    # -------------------------

    highest_price: float = 0.0

    lowest_price: float = 0.0

    trail_started: bool = False

    breakeven_done: bool = False