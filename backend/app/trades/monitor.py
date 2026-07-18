from app.live.redis_cache import LiveCache
from app.trades.cache import TradeCache
from app.trades.pnl import PnLCalculator


class TradeMonitor:

    @classmethod
    def update(
        cls,
        *,
        exchange: str,
        token: str,
        timeframe: str,
    ) -> None:

        trade = TradeCache.get(
            exchange=exchange,
            token=token,
            timeframe=timeframe,
        )

        if trade is None:
            return

        live = LiveCache.get(token)

        if live is None:
            return

        price = live["ltp"]

        state = trade["state"]

        if state in (
            "BUY_ACTIVE",
            "SELL_ACTIVE",
        ):

            trade["pnl"] = PnLCalculator.calculate(
                signal=trade["signal"],
                entry=trade["entry_price"],
                current=price,
                quantity=trade["quantity"],
            )

            if state == "BUY_ACTIVE":

                if price >= trade["target"]:
                    trade["state"] = "TARGET_HIT"
                    trade["exit_price"] = price
                    trade["reason"] = "TARGET"

                elif price <= trade["stop_loss"]:
                    trade["state"] = "STOPLOSS_HIT"
                    trade["exit_price"] = price
                    trade["reason"] = "STOPLOSS"

            elif state == "SELL_ACTIVE":

                if price <= trade["target"]:
                    trade["state"] = "TARGET_HIT"
                    trade["exit_price"] = price
                    trade["reason"] = "TARGET"

                elif price >= trade["stop_loss"]:
                    trade["state"] = "STOPLOSS_HIT"
                    trade["exit_price"] = price
                    trade["reason"] = "STOPLOSS"

        TradeCache.save(
            exchange=exchange,
            token=token,
            timeframe=timeframe,
            values=trade,
        )