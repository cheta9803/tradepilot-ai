from app.live.redis_cache import LiveCache


class LiveService:

    @staticmethod
    def get(
        token: str,
    ):
        return LiveCache.get(token)