from datetime import datetime

from app.core.config import settings
from app.trades.history_repository import TradeHistoryRepository


class RiskLimits:

    @classmethod
    def process(
        cls,
        *,
        trade: dict,
    ) -> None:
        """
        Placeholder for active-trade checks.
        Future account-level checks can be added here.
        """
        return

    @classmethod
    def daily_trade_limit_reached(cls) -> bool:
        """Prevent excessive completed trades in one session."""
        limit = settings.max_daily_trades
        if limit <= 0:
            return False
        return TradeHistoryRepository.get_today_trade_count() >= limit

    @classmethod
    def daily_loss_reached(cls) -> bool:
        """
        Returns True if today's gross realized loss
        reaches or exceeds the configured limit.

        Gross loss counts only losing trades.
        Profits do not offset losses.
        """

        total_loss = (
            TradeHistoryRepository.get_today_gross_loss()
        )

        return (
            total_loss
            >= settings.max_daily_loss
        )


    @classmethod
    def symbol_loss_cooldown_reached(
        cls,
        *,
        exchange: str,
        token: str,
    ) -> bool:
        """Block rapid re-entry on a symbol after its latest trade lost money."""

        cooldown_minutes = settings.symbol_loss_cooldown_minutes

        if cooldown_minutes <= 0:
            return False

        latest = TradeHistoryRepository.get_latest_closed_trade(
            exchange=exchange,
            token=token,
            timeframe="1m",
        )

        if latest is None or float(latest.pnl or 0.0) >= 0:
            return False

        closed_at = latest.closed_at

        if closed_at is None:
            return False

        now = datetime.now(
            closed_at.tzinfo
            if closed_at.tzinfo is not None
            else None
        )

        elapsed_seconds = (
            now - closed_at
        ).total_seconds()

        return elapsed_seconds < cooldown_minutes * 60

    @classmethod
    def loss_cooldown_reached(cls) -> bool:
        """
        Returns True while the configured consecutive-loss cooldown
        is active.

        Example:
            cooldown_after_losses = 3
            cooldown_minutes = 30

        Three consecutive losing completed trades start a 30-minute
        block on new entries. A profitable or break-even trade resets
        the consecutive-loss streak.
        """

        required_losses = settings.cooldown_after_losses
        cooldown_minutes = settings.cooldown_minutes

        if required_losses <= 0 or cooldown_minutes <= 0:
            return False

        streak, latest_loss_at = (
            TradeHistoryRepository.get_today_loss_streak()
        )

        if (
            streak < required_losses
            or latest_loss_at is None
        ):
            return False

        now = datetime.now(
            latest_loss_at.tzinfo
            if latest_loss_at.tzinfo is not None
            else None
        )

        elapsed_seconds = (
            now - latest_loss_at
        ).total_seconds()

        return (
            elapsed_seconds
            < cooldown_minutes * 60
        )
