import json
from datetime import datetime

from app.db.redis import redis_client


class StrategyCache:

    PREFIX = "strategy"

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
        values: dict,
    ) -> None:

        redis_client.set(
            cls._key(
                exchange,
                token,
                timeframe,
            ),
            json.dumps(
                {
                    **values,
                    "updated_at": datetime.now().isoformat(),
                }
            ),
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

        return json.loads(value)

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