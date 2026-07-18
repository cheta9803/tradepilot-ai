from datetime import datetime

from app.execution.capital import CapitalManager
from app.trades.lifecycle import TradeLifecycle
from app.trades.service import TradeService


class ExecutionEngine:

    @classmethod
    def process(cls) -> None:

        trades = TradeService.get_all()

        for trade in trades:

            if trade["state"] != "ENTRY_READY":
                continue

            invested = (
                trade["entry_price"]
                * trade["quantity"]
            )

            if not CapitalManager.has_capital(
                invested,
            ):
                continue

            if trade["signal"] == "BUY":

                TradeLifecycle.update(
                    exchange=trade["exchange"],
                    token=trade["token"],
                    timeframe=trade["timeframe"],
                    values={
                        "state": "BUY_ACTIVE",
                        "opened_at": datetime.now().isoformat(),
                    },
                )

                print(
                    f"BUY EXECUTED "
                    f"{trade['symbol']} "
                    f"{trade['timeframe']}"
                )

            elif trade["signal"] == "SELL":

                TradeLifecycle.update(
                    exchange=trade["exchange"],
                    token=trade["token"],
                    timeframe=trade["timeframe"],
                    values={
                        "state": "SELL_ACTIVE",
                        "opened_at": datetime.now().isoformat(),
                    },
                )

                print(
                    f"SELL EXECUTED "
                    f"{trade['symbol']} "
                    f"{trade['timeframe']}"
                )