from datetime import datetime

from app.candles.builder import CandleBuilder
from app.candles.redis_cache import CandleCache
from app.history.service import HistoryService
from app.instruments.cache import InstrumentCache


class HistoryLoader:

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

        candles = HistoryService.get_last_day(
            exchange=exchange,
            token=token,
        )

        if not candles:
            return

        last = candles[-1]

        candle = CandleBuilder.create(
            exchange=exchange,
            symbol=instrument.symbol,
            token=token,
            timeframe="1m",
            timestamp=datetime.fromisoformat(
                last[0],
            ).replace(
                second=0,
                microsecond=0,
            ),
            price=float(last[4]),
            volume=int(last[5]),
        )

        candle.open = float(last[1])
        candle.high = float(last[2])
        candle.low = float(last[3])
        candle.close = float(last[4])

        CandleCache.save(candle)

        print(
            f"Loaded history for {instrument.symbol}"
        )