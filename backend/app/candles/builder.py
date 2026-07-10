from datetime import datetime

from app.candles.models import Candle


class CandleBuilder:

    @staticmethod
    def create(
        *,
        exchange: str,
        symbol: str,
        token: str,
        timeframe: str,
        timestamp: datetime,
        price: float,
        volume: int,
    ) -> Candle:

        return Candle(
            exchange=exchange,
            symbol=symbol,
            token=token,
            timeframe=timeframe,
            timestamp=timestamp,
            open=price,
            high=price,
            low=price,
            close=price,
            volume=volume,
        )

    @staticmethod
    def update(
        candle: Candle,
        *,
        price: float,
        volume: int,
    ) -> Candle:

        candle.high = max(
            candle.high,
            price,
        )

        candle.low = min(
            candle.low,
            price,
        )

        candle.close = price

        candle.volume += volume

        return candle