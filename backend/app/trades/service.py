from app.db.redis import redis_client
from app.trades.cache import TradeCache


class TradeService:

    @classmethod
    def get_all(cls) -> list[dict]:

        trades = []

        for key in redis_client.scan_iter("trade:*"):

            value = redis_client.get(key)

            if value is None:
                continue

            trades.append(
                TradeCache.deserialize(value)
            )

        return sorted(
            trades,
            key=lambda trade: (
                trade["symbol"],
                trade["timeframe"],
            ),
        )

    @classmethod
    def get_open(cls) -> list[dict]:

        return [
            trade
            for trade in cls.get_all()
            if trade["state"] in (
                "ENTRY_READY",
                "BUY_ACTIVE",
                "SELL_ACTIVE",
            )
            and trade.get("order_status") != "FAILED"
        ]

    @classmethod
    def get_closed(cls) -> list[dict]:

        return [
            trade
            for trade in cls.get_all()
            if trade["state"] == "EXIT"
        ]

    @classmethod
    def get_symbol(
        cls,
        symbol: str,
    ) -> list[dict]:

        return [
            trade
            for trade in cls.get_all()
            if trade["symbol"] == symbol.upper()
        ]