from datetime import datetime

from app.candles.builder import CandleBuilder
from app.core.logger import logger
from app.history.redis_cache import HistoryCache
from app.history.service import HistoryService
from app.instruments.cache import InstrumentCache


class HistoryLoader:

    TIMEFRAME = "1m"

    @staticmethod
    def load(
        *,
        exchange: str,
        token: str,
    ) -> None:

        instrument = InstrumentCache.get_by_token(
            token,
        )

        if instrument is None:
            return

        latest = HistoryCache.get_latest_timestamp(
            exchange=exchange,
            token=token,
            timeframe=HistoryLoader.TIMEFRAME,
        )

        logger.debug(
            "%s: latest cached candle = %s",
            instrument.symbol,
            latest,
        )

        if latest is None:

            history = HistoryService.get_last_day(
                exchange=exchange,
                token=token,
            )

        else:

            history = HistoryService.get_since(
                exchange=exchange,
                token=token,
                from_date=latest,
            )

            #
            # Ignore duplicate last candle returned by API
            #
            if history:
                history = history[1:]

        if not history:
            return

        candles = []

        for row in history:

            candle = CandleBuilder.create(
                exchange=exchange,
                symbol=instrument.symbol,
                token=token,
                timeframe=HistoryLoader.TIMEFRAME,
                timestamp=datetime.fromisoformat(
                    row[0],
                ).replace(
                    second=0,
                    microsecond=0,
                ),
                price=float(row[4]),
                volume=int(row[5]),
            )

            candle.open = float(row[1])
            candle.high = float(row[2])
            candle.low = float(row[3])
            candle.close = float(row[4])

            candles.append(candle)

        if latest is None:

            HistoryCache.save(
                exchange=exchange,
                token=token,
                timeframe=HistoryLoader.TIMEFRAME,
                candles=candles,
            )

        else:

            for candle in candles:

                HistoryCache.append(
                    candle,
                )

        if latest is None:

            logger.info(
                "Loaded %d historical candles for %s",
                len(candles),
                instrument.symbol,
            )

        else:

            logger.info(
                "Synced %d new candles for %s",
                len(candles),
                instrument.symbol,
            )