from app.core.config import settings
from app.trades.lifecycle import TradeLifecycle


class BreakEvenStop:

    @classmethod
    def process(
        cls,
        *,
        trade: dict,
        ltp: float,
        atr: float,
    ) -> None:

        if not settings.breakeven_enabled:
            return

        if atr <= 0:
            return

        if trade.get("breakeven_done", False):
            return

        entry = trade["entry_price"]

        trigger = (
            atr
            * settings.breakeven_atr_multiplier
        )

        if trade["state"] == "BUY_ACTIVE":

            if ltp < entry + trigger:
                return

        elif trade["state"] == "SELL_ACTIVE":

            if ltp > entry - trigger:
                return

        else:
            return

        if abs(entry - trade["stop_loss"]) < settings.min_stop_move:
            return

        TradeLifecycle.update(
            exchange=trade["exchange"],
            token=trade["token"],
            timeframe=trade["timeframe"],
            values={
                "stop_loss": round(entry, 2),
                "breakeven_done": True,
            },
        )