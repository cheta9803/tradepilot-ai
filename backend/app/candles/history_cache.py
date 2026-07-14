import json

from app.db.redis import redis_client
from app.candles.models import Candle


class HistoryCache:

    PREFIX = "history"

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

        data = []

        for candle in candles:
            data.append(
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
            )

        redis_client.set(
            cls._key(
                exchange,
                token,
                timeframe,
            ),
            json.dumps(data),
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
            cls._key(
                exchange,
                token,
                timeframe,
            )
        )

        if value is None:
            return []

        rows = json.loads(value)

        candles = []

        for row in rows:
            candles.append(
                Candle(
                    exchange=row["exchange"],
                    symbol=row["symbol"],
                    token=row["token"],
                    timeframe=row["timeframe"],
                    timestamp=row["timestamp"],
                    open=row["open"],
                    high=row["high"],
                    low=row["low"],
                    close=row["close"],
                    volume=row["volume"],
                )
            )

        return candles

    @classmethod
    def delete(
        cls,
        *,
        exchange: str,
        token: str,
        timeframe: str,
    ) -> None:

        redis_client.delete(
            cls._key(
                exchange,
                token,
                timeframe,
            )
        )