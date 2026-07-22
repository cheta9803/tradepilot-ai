from dataclasses import dataclass


@dataclass(slots=True)
class Account:

    capital: float

    balance: float

    equity: float

    used_margin: float

    available_margin: float

    realized_pnl: float

    unrealized_pnl: float

    total_pnl: float