from datetime import datetime

from app.candles.builder import CandleBuilder
from app.core.logger import logger
from app.history.redis_cache import HistoryCache
from app.history.service import HistoryService
from app.instruments.cache import InstrumentCache


class HistoryLoader:

    TIMEFRAME = "1m"

    # 3,000 one-minute candles provide enough source data for 50 completed
    # 1-hour candles, which is the largest timeframe currently used by the
    # indicator/strategy pipeline.
    MIN_WARMUP_CANDLES = 3000

    @staticmethod
    def load(
        *,
        exchange: str,
        token: str,
        refresh: bool = False,
    ) -> None:

        instrument = InstrumentCache.get_by_token(token)
        if instrument is None:
            return

        existing = HistoryCache.get(
            exchange=exchange,
            token=token,
            timeframe=HistoryLoader.TIMEFRAME,
        )

        latest = (
            existing[-1].timestamp
            if existing
            else None
        )

        logger.debug(
            "%s: cached 1m candles=%d, latest=%s",
            instrument.symbol,
            len(existing),
            latest,
        )

        # A small DB cache is not sufficient for higher-timeframe indicators.
        # Fetch the full warm-up range instead of only requesting today's tail.
        needs_warmup = (
            refresh
            or latest is None
            or len(existing) < HistoryLoader.MIN_WARMUP_CANDLES
        )

        if needs_warmup:
            logger.info(
                "%s: history warm-up required. Cached 1m candles: %d",
                instrument.symbol,
                len(existing),
            )
            history = HistoryService.get_warmup(
                exchange=exchange,
                token=token,
            )
        else:
            history = HistoryService.get_since(
                exchange=exchange,
                token=token,
                from_date=latest,
            )

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
                timestamp=datetime.fromisoformat(row[0]).replace(
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

        if not candles:
            return

        by_timestamp = {
            candle.timestamp: candle
            for candle in existing
        }

        for candle in candles:
            by_timestamp[candle.timestamp] = candle

        merged = sorted(
            by_timestamp.values(),
            key=lambda candle: candle.timestamp,
        )

        HistoryCache.save(
            exchange=exchange,
            token=token,
            timeframe=HistoryLoader.TIMEFRAME,
            candles=merged,
        )

        logger.info(
            "%s: history cache now contains %d 1m candles",
            instrument.symbol,
            len(merged),
        )
