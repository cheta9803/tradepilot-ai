from datetime import datetime

from app.core.config import settings
from app.trades.cache import TradeCache


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
    def daily_loss_reached(cls) -> bool:
        """
        Returns True if today's realized loss
        exceeds the configured limit.
        """

        today = datetime.now().date()

        total_loss = 0.0

        for trade in TradeCache.get_all():

            closed_at = trade.get("closed_at")

            if not closed_at:
                continue

            try:
                closed_date = datetime.fromisoformat(closed_at).date()
            except (TypeError, ValueError):
                continue

            if closed_date != today:
                continue

            pnl = float(trade.get("pnl") or 0.0)

            if pnl < 0:
                total_loss += abs(pnl)

        return total_loss >= settings.max_daily_loss