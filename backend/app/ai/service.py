import json

from app.ai.cache import AICache
from app.db.redis import redis_client
from app.instruments.cache import InstrumentCache


class AIService:

    @classmethod
    def top_opportunities(
        cls,
        *,
        timeframe: str = "1m",
        limit: int = 10,
    ) -> list[dict]:

        opportunities = []

        pattern = f"ai:*:{timeframe}"

        for key in redis_client.scan_iter(match=pattern):

            if isinstance(key, bytes):
                key = key.decode()

            value = redis_client.get(key)

            if value is None:
                continue

            if isinstance(value, bytes):
                value = value.decode()

            ai = json.loads(value)

            _, exchange, token, timeframe = key.split(":")

            instrument = InstrumentCache.get_by_token(
                token=token,
            )

            if instrument is None:
                continue

            opportunities.append(
                {
                    "symbol": instrument.symbol,
                    "exchange": exchange,
                    "token": token,
                    **ai,
                }
            )

        opportunities.sort(
            key=lambda x: x["score"],
            reverse=True,
        )

        return opportunities[:limit]