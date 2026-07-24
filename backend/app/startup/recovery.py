from app.core.logger import logger
from app.trades.cache import TradeCache
from app.trades.models import Trade


class StartupRecovery:

    @classmethod
    def recover(cls) -> list[Trade]:
        logger.info("Starting trade recovery...")

        cached_trades = TradeCache.get_all()

        if not cached_trades:
            logger.info("No cached trades found.")
            return []

        recovered: list[Trade] = []

        for data in cached_trades:
            try:
                trade = Trade(**data)
                recovered.append(trade)

            except Exception:
                logger.exception(
                    "Failed to recover cached trade: %s",
                    data,
                )

        logger.info(
            "Recovered %d trade(s).",
            len(recovered),
        )

        return recovered