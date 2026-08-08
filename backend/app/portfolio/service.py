from app.core.config import settings
from app.portfolio.models import Portfolio
from app.trades.service import TradeService


class PortfolioService:

    @classmethod
    def summary(cls) -> Portfolio:

        trades = TradeService.get_all()

        invested = 0.0
        exposure = 0.0

        open_positions = 0
        closed_positions = 0

        realized_pnl = 0.0
        unrealized_pnl = 0.0

        for trade in trades:

            state = trade["state"]

            if state in (
                "ENTRY_READY",
                "BUY_ACTIVE",
                "SELL_ACTIVE",
            ):

                value = (
                    trade["entry_price"]
                    * trade["quantity"]
                )

                invested += value
                exposure += value

                open_positions += 1

                unrealized_pnl += trade.get(
                    "pnl",
                    0.0,
                )

            elif state == "EXIT":

                closed_positions += 1

                realized_pnl += trade.get(
                    "pnl",
                    0.0,
                )

        available = max(
            settings.default_capital - invested,
            0.0,
        )

        total_pnl = (
            realized_pnl
            + unrealized_pnl
        )

        return Portfolio(
            capital=settings.default_capital,
            invested=round(invested, 2),
            available=round(available, 2),
            exposure=round(exposure, 2),
            open_positions=open_positions,
            closed_positions=closed_positions,
            realized_pnl=round(realized_pnl, 2),
            unrealized_pnl=round(unrealized_pnl, 2),
            total_pnl=round(total_pnl, 2),
        )