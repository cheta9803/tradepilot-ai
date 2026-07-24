from datetime import datetime

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

        trade_data = TradeCache.get(
            exchange=exchange,
            token=token,
            timeframe=timeframe,
        )

        if trade_data is None:
            return

        live = LiveCache.get(token)

        if live is None:
            return

        trade = Trade(**trade_data)

        price = live["ltp"]

        trade.current_price = price

        if trade.state in (
            "BUY_ACTIVE",
            "SELL_ACTIVE",
        ):

            trade.pnl = PnLCalculator.calculate(
                signal=trade.signal,
                entry=trade.entry_price,
                current=price,
                quantity=trade.quantity,
            )

            if trade.state == "BUY_ACTIVE":

                if price >= trade.target:
                    trade.state = "TARGET_HIT"
                    trade.exit_price = price
                    trade.reason = "TARGET"
                    trade.closed_at = datetime.now().isoformat()

                elif price <= trade.stop_loss:
                    trade.state = "STOPLOSS_HIT"
                    trade.exit_price = price
                    trade.reason = "STOPLOSS"
                    trade.closed_at = datetime.now().isoformat()

            elif trade.state == "SELL_ACTIVE":

                if price <= trade.target:
                    trade.state = "TARGET_HIT"
                    trade.exit_price = price
                    trade.reason = "TARGET"
                    trade.closed_at = datetime.now().isoformat()

                elif price >= trade.stop_loss:
                    trade.state = "STOPLOSS_HIT"
                    trade.exit_price = price
                    trade.reason = "STOPLOSS"
                    trade.closed_at = datetime.now().isoformat()

        trade.updated_at = datetime.now().isoformat()

        TradeCache.save(
            trade=trade,
        )