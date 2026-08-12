from app.dashboard.models import (
    DashboardSummary,
    MarketIndex,
    Order,
    Position,
)


class DashboardMapper:

    @staticmethod
    def summary(
        portfolio,
        today_pnl: float,
    ) -> DashboardSummary:

        return DashboardSummary(
            portfolioValue=portfolio.capital,
            todayPnL=today_pnl,
            availableMargin=portfolio.available,
            openPositions=portfolio.open_positions,
        )

    @staticmethod
    def position(trade: dict) -> Position:

        return Position(
            symbol=trade["symbol"],
            quantity=trade["quantity"],
            averagePrice=trade["entry_price"],
            ltp=trade.get(
                "current_price",
                trade["entry_price"],
            ),
            pnl=trade.get(
                "pnl",
                0.0,
            ),
        )

    @staticmethod
    def order(trade: dict) -> Order:

        return Order(
            symbol=trade["symbol"],
            type=trade["signal"],
            quantity=trade["quantity"],
            status=trade["state"],
        )

    @staticmethod
    def market_index(
        *,
        name: str,
        live: dict | None,
    ) -> MarketIndex:

        if live is None:

            return MarketIndex(
                name=name,
                value=0.0,
                change=0.0,
                changePercent=0.0,
            )

        previous_close = live.get(
            "close",
            0.0,
        )

        change = (
            live["ltp"] - previous_close
            if previous_close
            else 0.0
        )

        change_percent = (
            (change / previous_close) * 100
            if previous_close
            else 0.0
        )

        return MarketIndex(
            name=name,
            value=live["ltp"],
            change=round(change, 2),
            changePercent=round(change_percent, 2),
        )