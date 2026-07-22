from pydantic import BaseModel


class PortfolioResponse(BaseModel):

    capital: float

    invested: float

    available: float

    exposure: float

    open_positions: int

    closed_positions: int

    realized_pnl: float

    unrealized_pnl: float

    total_pnl: float