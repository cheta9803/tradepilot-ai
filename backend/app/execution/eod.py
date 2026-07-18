from datetime import datetime
from zoneinfo import ZoneInfo

from app.core.config import settings
from app.live.redis_cache import LiveCache
from app.trades.lifecycle import TradeLifecycle
from app.trades.service import TradeService


class EndOfDayService:

    MARKET_TZ = ZoneInfo("Asia/Kolkata")

    @classmethod
    def should_square_off(cls) -> bool:

        now = datetime.now(cls.MARKET_TZ)

        return (
            now.hour > settings.market_close_hour
            or (
                now.hour == settings.market_close_hour
                and now.minute >= settings.market_close_minute
            )
        )

    @classmethod
    def square_off(cls) -> None:

        if not cls.should_square_off():
            return

        trades = TradeService.get_open()

        for trade in trades:

            if trade["state"] not in (
                "BUY_ACTIVE",
                "SELL_ACTIVE",
            ):
                continue

            live = LiveCache.get(trade["token"])

            if live is None:
                continue

            ltp = live["ltp"]

            if trade["signal"] == "BUY":

                pnl = (
                    ltp
                    - trade["entry_price"]
                ) * trade["quantity"]

            else:

                pnl = (
                    trade["entry_price"]
                    - ltp
                ) * trade["quantity"]

            TradeLifecycle.update(
                exchange=trade["exchange"],
                token=trade["token"],
                timeframe=trade["timeframe"],
                values={
                    "state": "EXIT",
                    "reason": "EOD",
                    "exit_price": round(ltp, 2),
                    "closed_at": datetime.now().isoformat(),
                    "current_price": round(ltp, 2),
                    "pnl": round(pnl, 2),
                },
            )

            print(
                f"EOD Square-Off "
                f"{trade['symbol']} "
                f"{trade['timeframe']}"
            )