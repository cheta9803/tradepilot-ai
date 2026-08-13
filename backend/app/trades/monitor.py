from datetime import UTC, datetime

from app.core.logger import logger
from app.live.redis_cache import LiveCache
from app.trades.cache import TradeCache
from app.trades.models import Trade
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

        try:

            trade_data = TradeCache.get(
                exchange=exchange,
                token=token,
                timeframe=timeframe,
            )

            if trade_data is None:
                return

            #
            # TradeMonitor only manages live market values.
            #
            # Exit decisions are handled centrally by
            # ExecutionService.
            #
            if trade_data["state"] not in (
                "BUY_ACTIVE",
                "SELL_ACTIVE",
            ):
                return

            live = LiveCache.get(token)

            if live is None:
                return

            trade = Trade(**trade_data)

            price = live["ltp"]

            trade.current_price = price

            trade.pnl = PnLCalculator.calculate(
                signal=trade.signal,
                entry=trade.entry_price,
                current=price,
                quantity=trade.quantity,
            )

            trade.updated_at = datetime.now(UTC).isoformat()

            TradeCache.save(
                trade=trade,
            )

        except Exception as exc:

            logger.warning(
                "Trade monitor update failed for %s/%s/%s: %s",
                exchange,
                token,
                timeframe,
                exc,
            )
