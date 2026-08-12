from datetime import datetime
import json

from app.db.redis import redis_client
from app.trades.cache import TradeCache
from app.trades.models import Trade
from app.core.market_session import MarketSession
from app.trades.history_repository import TradeHistoryRepository


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
        execution_mode: str = "PAPER",
    ) -> None:

        existing = TradeCache.get(
            exchange=exchange,
            token=token,
            timeframe=timeframe,
        )

        #
        # Never create LIVE trades outside market hours.
        #
        if (
            execution_mode == "LIVE"
            and not MarketSession.can_enter_trade()
        ):
            return

        #
        # Existing active trade.
        #
        if existing is not None:

            if existing["state"] in (
                "ENTRY_READY",
                "BUY_ACTIVE",
                "SELL_ACTIVE",
            ):
                return

            #
            # Old trade finished.
            # Remove it completely.
            #
            TradeCache.delete(
                exchange=exchange,
                token=token,
                timeframe=timeframe,
            )

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
            execution_mode=execution_mode,

            #
            # Risk State
            #
            highest_price=entry,
            lowest_price=entry,
            trail_started=False,
            breakeven_done=False,
        )

        TradeCache.save(
            trade=trade,
        )

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

        #
        # Entry activated
        #
        if (
            previous_state == "ENTRY_READY"
            and current_state in (
                "BUY_ACTIVE",
                "SELL_ACTIVE",
            )
            and trade.get("opened_at") is None
        ):
            trade["opened_at"] = now

        #
        # Trade completed
        #
        trade_closed_now = (
            previous_state != "EXIT"
            and current_state == "EXIT"
        )

        if trade_closed_now:

            if trade.get("closed_at") is None:
                trade["closed_at"] = now

            TradeHistoryRepository.create_from_trade(
                trade,
            )

        #
        # Failed / cancelled / rejected
        #
        if (
            current_state in (
                "ENTRY_FAILED",
                "REJECTED",
                "CANCELLED",
            )
            and trade.get("closed_at") is None
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

    @classmethod
    def delete(
        cls,
        *,
        exchange: str,
        token: str,
        timeframe: str,
    ) -> None:

        TradeCache.delete(
            exchange=exchange,
            token=token,
            timeframe=timeframe,
        )