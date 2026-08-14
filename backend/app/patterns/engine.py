from app.indicators.repository import IndicatorRepository
from app.instruments.cache import InstrumentCache
from app.patterns.cache import PatternCache
from app.patterns.service import PatternService


class PatternEngine:

    @classmethod
    def calculate(
        cls,
        *,
        exchange: str,
        token: str,
        timeframe: str,
    ) -> None:

        instrument = InstrumentCache.get_by_token(
            token
        )

        if instrument is None:
            return

        repository = IndicatorRepository()

        candles = repository.get_candles(
            symbol=instrument.symbol,
            timeframe=timeframe,
        )

        if len(candles) < 20:
            return

        result = PatternService.analyze(
            candles
        )

        result.candle_timestamp = candles[-1].timestamp.isoformat()

        PatternCache.save(
            exchange=exchange,
            token=token,
            timeframe=timeframe,
            result=result,
        )