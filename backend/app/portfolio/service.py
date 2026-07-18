from app.portfolio.models import Portfolio
from app.trades.service import TradeService


class PortfolioService:

    DEFAULT_CAPITAL = 100000.0

    @classmethod
    def summary(cls) -> Portfolio:

        trades = TradeService.get_all()

        invested = 0.0
        open_positions = 0
        closed_positions = 0
        realized_pnl = 0.0
        unrealized_pnl = 0.0

        for trade in trades:

            state = trade["state"]

            if state in (
                "BUY_ACTIVE",
                "SELL_ACTIVE",
                "ENTRY_READY",
            ):

                invested += (
                    trade["entry_price"]
                    * trade["quantity"]
                )

                open_positions += 1

            elif state == "EXIT":

                closed_positions += 1

                realized_pnl += trade["pnl"]

        available = (
            cls.DEFAULT_CAPITAL
            - invested
        )

        total_pnl = (
            realized_pnl
            + unrealized_pnl
        )

        return Portfolio(
            capital=cls.DEFAULT_CAPITAL,
            invested=round(invested, 2),
            available=round(available, 2),
            open_positions=open_positions,
            closed_positions=closed_positions,
            realized_pnl=round(realized_pnl, 2),
            unrealized_pnl=round(unrealized_pnl, 2),
            total_pnl=round(total_pnl, 2),
        )