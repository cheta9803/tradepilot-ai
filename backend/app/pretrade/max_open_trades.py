from app.core.config import settings
from app.trades.cache import TradeCache


class MaxOpenTradesPolicy:
    """
    Checks whether the maximum number of
    active positions has been reached.
    """

    ACTIVE_STATES = {
        "BUY_ACTIVE",
        "SELL_ACTIVE",
    }

    @classmethod
    def reached(cls) -> bool:

        trades = TradeCache.get_all()

        active_trades = sum(
            1
            for trade in trades
            if trade.get("state") in cls.ACTIVE_STATES
        )

        return (
            active_trades
            >= settings.max_open_trades
        )