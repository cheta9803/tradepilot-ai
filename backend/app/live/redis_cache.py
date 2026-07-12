import json

from app.db.redis import redis_client

class LiveCache:

    PREFIX = "live"

    @classmethod
    def save(
        cls,
        token: str,
        data: dict,
    ):

        redis_client.set(
            f"{cls.PREFIX}:{token}",
            json.dumps(
                {
                    **data,
                    "timestamp": data["timestamp"].isoformat(),
                }
            )
        )

    @classmethod
    def get(
        cls,
        token: str,
    ):

        value = redis_client.get(
            f"{cls.PREFIX}:{token}",
        )

        if value is None:
            return None

        return json.loads(value)