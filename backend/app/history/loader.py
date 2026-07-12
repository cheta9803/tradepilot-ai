from datetime import datetime

from app.candles.builder import CandleBuilder
from app.candles.redis_cache import CandleCache
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

        history = HistoryService.get_last_day(
            exchange=exchange,
            token=token,
        )

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

        HistoryCache.save(
            exchange=exchange,
            token=token,
            timeframe=HistoryLoader.TIMEFRAME,
            candles=candles,
        )

        print(
            f"Loaded {len(candles)} candles for "
            f"{instrument.symbol}"
        )