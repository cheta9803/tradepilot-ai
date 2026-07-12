from app.candles.models import Candle
from app.history.redis_cache import HistoryCache
from app.instruments.cache import InstrumentCache


class IndicatorRepository:

    TIMEFRAME = "1m"

    @staticmethod
    def get_candles(
        *,
        symbol: str,
        timeframe: str,
    ) -> list[Candle]:

        instrument = InstrumentCache.get_by_symbol(
            exchange="NSE",
            symbol=symbol,
        )

        if instrument is None:
            raise ValueError(
                f"Instrument '{symbol}' not found."
            )

        candles = HistoryCache.get(
            exchange=instrument.exchange,
            token=instrument.token,
            timeframe=timeframe,
        )

        if not candles:
            raise ValueError(
                f"No candle history found for '{symbol}'."
            )

        return candles