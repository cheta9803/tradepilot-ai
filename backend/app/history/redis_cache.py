import json
from datetime import datetime

from app.candles.models import Candle
from app.db.redis import redis_client


class HistoryCache:

    PREFIX = "history"

    MAX_CANDLES = 375

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

        redis_client.set(
            cls._key(
                exchange,
                token,
                timeframe,
            ),
            json.dumps(
                [
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
                ]
            ),
        )

    @classmethod
    def append(
        cls,
        candle: Candle,
    ) -> None:

        candles = cls.get(
            exchange=candle.exchange,
            token=candle.token,
            timeframe=candle.timeframe,
        )

        if candles:

            last = candles[-1]

            if last.timestamp == candle.timestamp:
                candles[-1] = candle
            else:
                candles.append(candle)

        else:
            candles.append(candle)

        candles = candles[-cls.MAX_CANDLES :]

        cls.save(
            exchange=candle.exchange,
            token=candle.token,
            timeframe=candle.timeframe,
            candles=candles,
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

        data = json.loads(value)

        candles = []

        for item in data:

            candles.append(
                Candle(
                    exchange=item["exchange"],
                    symbol=item["symbol"],
                    token=item["token"],
                    timeframe=item["timeframe"],
                    timestamp=datetime.fromisoformat(
                        item["timestamp"],
                    ),
                    open=item["open"],
                    high=item["high"],
                    low=item["low"],
                    close=item["close"],
                    volume=item["volume"],
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