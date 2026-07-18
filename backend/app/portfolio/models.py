from dataclasses import dataclass


@dataclass(slots=True)
class Portfolio:

    capital: float

    invested: float

    available: float

    open_positions: int

    closed_positions: int

    realized_pnl: float

    unrealized_pnl: float

    total_pnl: float