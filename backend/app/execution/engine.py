from app.portfolio.service import PortfolioService
from app.trades.lifecycle import TradeLifecycle
from app.trades.service import TradeService


class ExecutionEngine:

    @classmethod
    def process(cls) -> None:

        trades = TradeService.get_all()

        portfolio = PortfolioService.summary()

        available = portfolio.available

        for trade in trades:

            if trade["state"] != "ENTRY_READY":
                continue

            required = (
                trade["entry_price"]
                * trade["quantity"]
            )

            if required > available:

                continue

            available -= required

            if trade["signal"] == "BUY":

                TradeLifecycle.update(
                    exchange=trade["exchange"],
                    token=trade["token"],
                    timeframe=trade["timeframe"],
                    values={
                        "state": "BUY_ACTIVE",
                    },
                )

            elif trade["signal"] == "SELL":

                TradeLifecycle.update(
                    exchange=trade["exchange"],
                    token=trade["token"],
                    timeframe=trade["timeframe"],
                    values={
                        "state": "SELL_ACTIVE",
                    },
                )