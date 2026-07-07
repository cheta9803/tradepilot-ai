from app.live.manager import LiveManager


class SubscriptionManager:

    _subscriptions: dict[str, dict] = {}

    _manager = LiveManager()

    @classmethod
    def subscribe(
        cls,
        exchange: str,
        token: str,
    ):

        if token in cls._subscriptions:
            cls._subscriptions[token]["count"] += 1
            return

        cls._manager.subscribe(
            exchange=exchange,
            token=token,
        )

        cls._subscriptions[token] = {
            "exchange": exchange,
            "count": 1,
        }

    @classmethod
    def unsubscribe(
        cls,
        token: str,
    ):

        subscription = cls._subscriptions.get(token)

        if subscription is None:
            return

        subscription["count"] -= 1

        if subscription["count"] > 0:
            return

        cls._manager.unsubscribe(
            exchange=subscription["exchange"],
            token=token,
        )

        del cls._subscriptions[token]

    @classmethod
    def is_subscribed(
        cls,
        token: str,
    ) -> bool:

        return token in cls._subscriptions

    @classmethod
    def active_count(cls) -> int:
        return len(cls._subscriptions)

    @classmethod
    def get_active_tokens(cls):

        return list(cls._subscriptions.keys())