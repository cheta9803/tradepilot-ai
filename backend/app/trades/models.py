from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Trade:

    exchange: str

    token: str

    symbol: str

    timeframe: str

    risk_timeframe: str = "1m"

    state: str = ""

    signal: str = ""

    entry_price: float = 0.0

    stop_loss: float = 0.0

    target: float = 0.0

    quantity: int = 0

    opened_at: str | None = None

    closed_at: str | None = None

    exit_price: float | None = None

    pnl: float = 0.0

    current_price: float = 0.0

    reason: str | None = None

    updated_at: str = datetime.now().isoformat()

    # -------------------------
    # Broker Order
    # -------------------------

    order_id: str | None = None

    order_role: str = "ENTRY"

    order_status: str | None = None

    broker: str | None = None

    execution_mode: str = "PAPER"

    # -------------------------
    # Risk State
    # -------------------------

    highest_price: float = 0.0

    lowest_price: float = 0.0

    trail_started: bool = False

    breakeven_done: bool = False

    # Identifies what kind of stop is currently active.
    # This is used when a stop is hit so history can distinguish
    # the original stop from a trailing or break-even stop.
    stop_reason: str = "STOPLOSS"
