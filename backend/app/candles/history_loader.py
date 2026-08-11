from sqlalchemy.orm import Session

from app.candles.repository import CandleRepository
from app.core.logger import logger
from app.history.redis_cache import HistoryCache


class CandleHistoryLoader:

    # Maximum number of candles retained per
    # exchange/token/timeframe combination.
    LIMIT = 3000

    @staticmethod
    def load(
        db: Session,
    ) -> None:

        grouped = CandleRepository.load_recent_grouped(
            db=db,
            limit=CandleHistoryLoader.LIMIT,
        )

        if not grouped:

            logger.info(
                "No persisted candle history found."
            )

            return

        total_groups = len(grouped)

        logger.info(
            "Loading persisted candle history "
            "for %d instrument/timeframe groups.",
            total_groups,
        )

        for (
            exchange,
            token,
            timeframe,
        ), candles in grouped.items():

            if not candles:
                continue

            HistoryCache.save(
                exchange=exchange,
                token=token,
                timeframe=timeframe,
                candles=candles,
            )

            logger.info(
                "Loaded %d historical candles "
                "for %s:%s:%s",
                len(candles),
                exchange,
                token,
                timeframe,
            )

        logger.info(
            "Persisted candle history loading completed."
        )