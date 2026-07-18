from datetime import datetime

from app.live.redis_cache import LiveCache
from app.trades.lifecycle import TradeLifecycle
from app.trades.service import TradeService


class ExecutionService:

    @classmethod
    def process(cls) -> None:

        trades = TradeService.get_open()

        for trade in trades:

            live = LiveCache.get(trade["token"])

            if live is None:
                continue

            ltp = live["ltp"]

            state = trade["state"]

            if state == "ENTRY_READY":

                cls._process_entry(
                    trade,
                    ltp,
                )

            elif state in (
                "BUY_ACTIVE",
                "SELL_ACTIVE",
            ):

                cls._update_live_pnl(
                    trade,
                    ltp,
                )

                cls._process_exit(
                    trade,
                    ltp,
                )

    @classmethod
    def _update_live_pnl(
        cls,
        trade: dict,
        ltp: float,
    ) -> None:

        if trade["signal"] == "BUY":

            pnl = (
                ltp - trade["entry_price"]
            ) * trade["quantity"]

        else:

            pnl = (
                trade["entry_price"] - ltp
            ) * trade["quantity"]

        TradeLifecycle.update(
            exchange=trade["exchange"],
            token=trade["token"],
            timeframe=trade["timeframe"],
            values={
                "current_price": round(ltp, 2),
                "pnl": round(pnl, 2),
            },
        )

    @classmethod
    def _process_entry(
        cls,
        trade: dict,
        ltp: float,
    ) -> None:

        signal = trade["signal"]

        activate = False

        if signal == "BUY" and ltp >= trade["entry_price"]:
            activate = True

        elif signal == "SELL" and ltp <= trade["entry_price"]:
            activate = True

        if not activate:
            return

        TradeLifecycle.update(
            exchange=trade["exchange"],
            token=trade["token"],
            timeframe=trade["timeframe"],
            values={
                "state": (
                    "BUY_ACTIVE"
                    if signal == "BUY"
                    else "SELL_ACTIVE"
                ),
                "opened_at": datetime.now().isoformat(),
            },
        )

        print(
            f"Trade Activated "
            f"{trade['symbol']} "
            f"{trade['timeframe']}"
        )

    @classmethod
    def _process_exit(
        cls,
        trade: dict,
        ltp: float,
    ) -> None:

        if trade["closed_at"] is not None:
            return

        signal = trade["signal"]

        exit_reason = None

        if signal == "BUY":

            if ltp >= trade["target"]:
                exit_reason = "TARGET"

            elif ltp <= trade["stop_loss"]:
                exit_reason = "STOPLOSS"

        else:

            if ltp <= trade["target"]:
                exit_reason = "TARGET"

            elif ltp >= trade["stop_loss"]:
                exit_reason = "STOPLOSS"

        if exit_reason is None:
            return

        pnl = (
            (ltp - trade["entry_price"])
            * trade["quantity"]
        )

        if signal == "SELL":
            pnl *= -1

        TradeLifecycle.update(
            exchange=trade["exchange"],
            token=trade["token"],
            timeframe=trade["timeframe"],
            values={
                "state": "EXIT",
                "closed_at": datetime.now().isoformat(),
                "exit_price": ltp,
                "reason": exit_reason,
                "pnl": round(pnl, 2),
                "current_price": round(ltp, 2),
            },
        )

        print(
            f"Trade Closed "
            f"{trade['symbol']} "
            f"{exit_reason}"
        )