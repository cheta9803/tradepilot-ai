from datetime import datetime
import json

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

        existing = TradeCache.get(
            exchange=exchange,
            token=token,
            timeframe=timeframe,
        )

        if existing:

            if existing["state"] in (
                "BUY_ACTIVE",
                "SELL_ACTIVE",
            ):
                return

            if existing["state"] in (
                "WAIT",
                "ENTRY_READY",
            ):

                existing.update(
                    {
                        "signal": signal,
                        "state": state,
                        "entry_price": entry,
                        "stop_loss": stop_loss,
                        "target": target,
                        "quantity": quantity,

                        # -------------------------
                        # Reset Risk State
                        # -------------------------
                        "highest_price": entry,
                        "lowest_price": entry,
                        "trail_started": False,
                        "breakeven_done": False,

                        "updated_at": datetime.now().isoformat(),
                    }
                )

                redis_client.set(
                    TradeCache._key(
                        exchange,
                        token,
                        timeframe,
                    ),
                    json.dumps(existing),
                )

                return

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

            # -------------------------
            # Risk State
            # -------------------------
            highest_price=entry,
            lowest_price=entry,
            trail_started=False,
            breakeven_done=False,
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

        previous_state = trade["state"]

        trade.update(values)

        current_state = trade["state"]

        now = datetime.now().isoformat()

        if (
            previous_state == "ENTRY_READY"
            and current_state in (
                "BUY_ACTIVE",
                "SELL_ACTIVE",
            )
            and trade["opened_at"] is None
        ):
            trade["opened_at"] = now

        if (
            current_state == "EXIT"
            and trade["closed_at"] is None
        ):
            trade["closed_at"] = now

        trade["updated_at"] = now

        redis_client.set(
            TradeCache._key(
                exchange,
                token,
                timeframe,
            ),
            json.dumps(trade),
        )

    @classmethod
    def get(
        cls,
        *,
        exchange: str,
        token: str,
        timeframe: str,
    ) -> dict | None:

        return TradeCache.get(
            exchange=exchange,
            token=token,
            timeframe=timeframe,
        )