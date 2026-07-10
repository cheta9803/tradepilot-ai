import json

from app.candles.models import Candle
from app.live.redis_cache import redis_client
from datetime import datetime


class CandleCache:

    PREFIX = "candle"

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
        candle: Candle,
    ) -> None:

        redis_client.set(
            cls._key(
                exchange=candle.exchange,
                token=candle.token,
                timeframe=candle.timeframe,
            ),
            json.dumps(
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
            ),
        )

    @classmethod
    def get(
        cls,
        exchange: str,
        token: str,
        timeframe: str,
    ) -> Candle | None:

        value = redis_client.get(
            cls._key(
                exchange=exchange,
                token=token,
                timeframe=timeframe,
            )
        )

        if value is None:
            return None

        data = json.loads(value)

        return Candle(
            exchange=data["exchange"],
            symbol=data["symbol"],
            token=data["token"],
            timeframe=data["timeframe"],
            timestamp=datetime.fromisoformat(
                data["timestamp"]
            ),
            open=data["open"],
            high=data["high"],
            low=data["low"],
            close=data["close"],
            volume=data["volume"],
        )

    @classmethod
    def delete(
        cls,
        exchange: str,
        token: str,
        timeframe: str,
    ) -> None:

        redis_client.delete(
            cls._key(
                exchange=exchange,
                token=token,
                timeframe=timeframe,
            )
        )