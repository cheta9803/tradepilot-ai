from datetime import datetime

from app.candles.builder import CandleBuilder
from app.candles.models import Candle
from app.candles.redis_cache import CandleCache


class CandleService:

    TIMEFRAME = "1m"

    @staticmethod
    def process_tick(
        *,
        exchange: str,
        symbol: str,
        token: str,
        price: float,
        volume: int,
        timestamp: datetime,
    ) -> None:

        candle = CandleCache.get(
            exchange=exchange,
            token=token,
            timeframe=CandleService.TIMEFRAME,
        )

        minute = timestamp.replace(
            second=0,
            microsecond=0,
        )

        if candle is None:

            candle = CandleBuilder.create(
                exchange=exchange,
                symbol=symbol,
                token=token,
                timeframe=CandleService.TIMEFRAME,
                timestamp=minute,
                price=price,
                volume=volume,
            )

            CandleCache.save(candle)

            return

        candle_time = candle.timestamp

        if isinstance(
            candle_time,
            str,
        ):
            candle_time = datetime.fromisoformat(
                candle_time,
            )

        if candle_time != minute:

            candle = CandleBuilder.create(
                exchange=exchange,
                symbol=symbol,
                token=token,
                timeframe=CandleService.TIMEFRAME,
                timestamp=minute,
                price=price,
                volume=volume,
            )

            CandleCache.save(candle)

            return

        candle = CandleBuilder.update(
            candle,
            price=price,
            volume=volume,
        )

        CandleCache.save(candle)