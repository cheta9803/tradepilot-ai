import json
from dataclasses import asdict
from datetime import datetime

from app.db.redis import redis_client
from app.ai.models import AIScore


class AICache:

    PREFIX = "ai"

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
        score: AIScore,
    ) -> None:

        values = asdict(score)

        values["updated_at"] = (
            datetime.now().isoformat()
        )

        redis_client.set(
            cls._key(
                exchange,
                token,
                timeframe,
            ),
            json.dumps(values),
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

        if isinstance(value, bytes):
            value = value.decode()

        return json.loads(value)