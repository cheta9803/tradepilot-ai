import json
from datetime import datetime

from app.candles.models import Candle
from app.db.redis import redis_client


class HistoryCache:

    PREFIX = "history"

    # Enough 1m candles for 50 x 1h indicators with warm-up headroom.
    MAX_CANDLES = 4000

    @classmethod
    def _key(
        cls,
        exchange: str,
        token: str,
        timeframe: str,
    ) -> str:

        return (
            f"{cls.PREFIX}:"
            f"{exchange}:"
            f"{token}:"
            f"{timeframe}"
        )

    @classmethod
    def save(
        cls,
        *,
        exchange: str,
        token: str,
        timeframe: str,
        candles: list[Candle],
    ) -> None:

        candles = sorted(
            candles,
            key=lambda candle: candle.timestamp,
        )[-cls.MAX_CANDLES:]

        redis_client.set(
            cls._key(exchange, token, timeframe),
            json.dumps([
                {
                    "exchange": candle.exchange,
                    "symbol": candle.symbol,
                    "token": candle.token,
                    "timeframe": candle.timeframe,
                    "timestamp": candle.timestamp.isoformat(),
                    "open": candle.open,
                    "high": candle.high,
                    "low": candle.low,
                    "close": candle.close,
                    "volume": candle.volume,
                }
                for candle in candles
            ]),
        )

    @classmethod
    def append(cls, candle: Candle) -> None:

        candles = cls.get(
            exchange=candle.exchange,
            token=candle.token,
            timeframe=candle.timeframe,
        )

        by_timestamp = {
            item.timestamp: item
            for item in candles
        }
        by_timestamp[candle.timestamp] = candle

        cls.save(
            exchange=candle.exchange,
            token=candle.token,
            timeframe=candle.timeframe,
            candles=list(by_timestamp.values()),
        )

    @classmethod
    def get(
        cls,
        *,
        exchange: str,
        token: str,
        timeframe: str,
    ) -> list[Candle]:

        value = redis_client.get(
            cls._key(exchange, token, timeframe),
        )

        if value is None:
            return []

        data = json.loads(value)

        return [
            Candle(
                exchange=item["exchange"],
                symbol=item["symbol"],
                token=item["token"],
                timeframe=item["timeframe"],
                timestamp=datetime.fromisoformat(item["timestamp"]),
                open=item["open"],
                high=item["high"],
                low=item["low"],
                close=item["close"],
                volume=item["volume"],
            )
            for item in data
        ]

    @classmethod
    def delete(
        cls,
        *,
        exchange: str,
        token: str,
        timeframe: str,
    ) -> None:

        redis_client.delete(
            cls._key(exchange, token, timeframe),
        )

    @classmethod
    def get_latest_timestamp(
        cls,
        *,
        exchange: str,
        token: str,
        timeframe: str,
    ) -> datetime | None:

        candles = cls.get(
            exchange=exchange,
            token=token,
            timeframe=timeframe,
        )

        if not candles:
            return None

        return candles[-1].timestamp
