from app.core.config import settings
from app.execution.order_service import ExecutionOrderService
from app.live.redis_cache import LiveCache
from app.trades.service import TradeService


class EndOfDayService:

    @classmethod
    def should_square_off(cls) -> bool:

        from datetime import datetime
        from zoneinfo import ZoneInfo

        market_tz = ZoneInfo("Asia/Kolkata")

        now = datetime.now(market_tz)

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

            #
            # Do not submit another EOD exit if an exit
            # order is already waiting.
            #
            if (
                trade.get("order_role") == "EXIT"
                and trade.get("order_status") in (
                    "PENDING",
                    "OPEN",
                )
            ):
                continue

            live = LiveCache.get(
                trade["token"]
            )

            if live is None:
                continue

            ltp = float(live["ltp"])

            success = ExecutionOrderService.execute_exit(
                trade=trade,
                exit_price=ltp,
                reason="EOD",
            )

            if success:

                print(
                    f"EOD Square-Off "
                    f"{trade['symbol']} "
                    f"{trade['timeframe']}"
                )