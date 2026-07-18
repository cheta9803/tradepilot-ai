import json
from datetime import datetime

from app.db.redis import redis_client
from app.trades.models import Trade


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

        redis_client.set(
            cls._key(
                trade.exchange,
                trade.token,
                trade.timeframe,
            ),
            json.dumps(
                {
                    "exchange": trade.exchange,
                    "token": trade.token,
                    "symbol": trade.symbol,
                    "timeframe": trade.timeframe,
                    "state": trade.state,
                    "signal": trade.signal,
                    "entry_price": trade.entry_price,
                    "stop_loss": trade.stop_loss,
                    "target": trade.target,
                    "quantity": trade.quantity,
                    "opened_at": (
                        trade.opened_at.isoformat()
                        if trade.opened_at
                        else None
                    ),
                    "closed_at": (
                        trade.closed_at.isoformat()
                        if trade.closed_at
                        else None
                    ),
                    "exit_price": trade.exit_price,
                    "pnl": trade.pnl,
                    "reason": trade.reason,
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

        return cls.deserialize(value)

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