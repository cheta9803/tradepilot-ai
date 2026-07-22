import json
from dataclasses import asdict
from datetime import datetime

from app.db.redis import redis_client
from app.trades.models import Trade

from typing import Any


class TradeCache:

    PREFIX = "trade"

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
        trade: Trade,
    ) -> None:

        data = asdict(trade)

        data["updated_at"] = datetime.now().isoformat()

        redis_client.set(
            cls._key(
                trade.exchange,
                trade.token,
                trade.timeframe,
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
    ) -> dict | None:

        value = redis_client.get(
            cls._key(
                exchange,
                token,
                timeframe,
            )
        )

        if value is None:
            return None

        return cls.deserialize(value)

    @classmethod
    def get_all(cls) -> list[dict[str, Any]]:
        """
        Return all cached trades.
        """

        pattern = f"{cls.PREFIX}:*"

        keys = redis_client.keys(pattern)

        if not keys:
            return []

        trades: list[dict[str, Any]] = []

        for key in keys:

            value = redis_client.get(key)

            if value is None:
                continue

            trades.append(cls.deserialize(value))

        return trades

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

    @classmethod
    def deserialize(
        cls,
        value: str | bytes,
    ) -> dict:

        if isinstance(value, bytes):
            value = value.decode()

        return json.loads(value)