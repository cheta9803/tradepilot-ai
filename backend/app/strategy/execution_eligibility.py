from datetime import UTC, datetime

from app.core.market_session import MarketSession
from app.pretrade.engine import PreTradeRiskEngine
from app.trades.cache import TradeCache
from app.trades.history_repository import TradeHistoryRepository


class TradeExecutionEligibility:
    """Explain whether a strategy-ready trade can actually be created.

    This is intentionally read-only. It mirrors the final gates used by
    StrategyEngine so the scanner/dashboard cannot show TRADE when the
    execution path would immediately reject the opportunity.
    """

    ACTIVE_STATES = {
        "ENTRY_READY",
        "BUY_ACTIVE",
        "SELL_ACTIVE",
    }

    @classmethod
    def evaluate(
        cls,
        *,
        exchange: str,
        token: str,
        trigger_candle_timestamp: str | None,
    ) -> dict:
        if not MarketSession.can_enter_trade():
            return cls._blocked(
                "Market is closed. New trades are not executable."
            )

        existing_trade = TradeCache.get(
            exchange=exchange,
            token=token,
            timeframe="1m",
        )

        if (
            existing_trade is not None
            and existing_trade.get("state") in cls.ACTIVE_STATES
        ):
            return cls._blocked(
                "An existing 1m trade is already active or ready."
            )

        if cls._trigger_already_consumed(
            exchange=exchange,
            token=token,
            trigger_candle_timestamp=trigger_candle_timestamp,
        ):
            return cls._blocked(
                "Fresh 1m trigger required: the latest trigger candle "
                "has already been consumed."
            )

        allowed, reason = PreTradeRiskEngine.evaluate(
            exchange=exchange,
            token=token,
        )

        if not allowed:
            return cls._blocked(reason)

        return {
            "execution_ready": True,
            "execution_block_reason": None,
        }

    @classmethod
    def _trigger_already_consumed(
        cls,
        *,
        exchange: str,
        token: str,
        trigger_candle_timestamp: str | None,
    ) -> bool:
        if not trigger_candle_timestamp:
            return False

        latest_closed = TradeHistoryRepository.get_latest_closed_trade(
            exchange=exchange,
            token=token,
            timeframe="1m",
        )

        if latest_closed is None or latest_closed.closed_at is None:
            return False

        trigger_at = datetime.fromisoformat(
            trigger_candle_timestamp,
        )

        if trigger_at.tzinfo is None:
            trigger_at = trigger_at.replace(tzinfo=UTC)

        closed_at = latest_closed.closed_at

        if closed_at.tzinfo is None:
            closed_at = closed_at.replace(tzinfo=UTC)

        return closed_at >= trigger_at

    @staticmethod
    def _blocked(reason: str) -> dict:
        return {
            "execution_ready": False,
            "execution_block_reason": reason,
        }
