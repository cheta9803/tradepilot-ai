from datetime import datetime

from app.db.redis import redis_client
from app.trades.cache import TradeCache
from app.trades.models import Trade


class TradeLifecycle:

    @classmethod
    def create(
        cls,
        *,
        exchange: str,
        token: str,
        symbol: str,
        timeframe: str,
        signal: str,
        state: str,
        entry: float,
        stop_loss: float,
        target: float,
        quantity: int,
    ) -> None:

        trade = Trade(
            exchange=exchange,
            token=token,
            symbol=symbol,
            timeframe=timeframe,
            state=state,
            signal=signal,
            entry_price=entry,
            stop_loss=stop_loss,
            target=target,
            quantity=quantity,
        )

        TradeCache.save(trade=trade)

    @classmethod
    def update(
        cls,
        *,
        exchange: str,
        token: str,
        timeframe: str,
        values: dict,
    ) -> None:

        trade = TradeCache.get(
            exchange=exchange,
            token=token,
            timeframe=timeframe,
        )

        if trade is None:
            return

        trade.update(values)
        trade["updated_at"] = datetime.now().isoformat()

        redis_client.set(
            TradeCache._key(
                exchange,
                token,
                timeframe,
            ),
            __import__("json").dumps(trade),
        )