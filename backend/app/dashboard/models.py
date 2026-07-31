from dataclasses import dataclass


@dataclass(slots=True)
class DashboardSummary:
    portfolioValue: float
    todayPnL: float
    availableMargin: float
    openPositions: int


@dataclass(slots=True)
class MarketIndex:
    name: str
    value: float
    change: float
    changePercent: float


@dataclass(slots=True)
class Position:
    symbol: str
    quantity: int
    averagePrice: float
    ltp: float
    pnl: float


@dataclass(slots=True)
class Order:
    symbol: str
    type: str
    quantity: int
    status: str


@dataclass(slots=True)
class DashboardResponse:
    summary: DashboardSummary
    indices: list[MarketIndex]
    positions: list[Position]
    orders: list[Order]