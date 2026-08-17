from app.pretrade.max_open_trades import MaxOpenTradesPolicy
from app.risk.limits import RiskLimits


class PreTradeRiskEngine:
    """Evaluate account-level checks before a new trade is created."""

    @classmethod
    def evaluate(
        cls,
        *,
        exchange: str | None = None,
        token: str | None = None,
    ) -> tuple[bool, str | None]:
        if RiskLimits.daily_trade_limit_reached():
            return (
                False,
                "Maximum completed trades for today reached. New trades are blocked.",
            )

        if RiskLimits.daily_loss_reached():
            return (
                False,
                "Daily loss limit reached. New trades are blocked.",
            )

        if RiskLimits.loss_cooldown_reached():
            return (
                False,
                "Consecutive-loss cooldown active. New trades are blocked.",
            )

        if exchange is not None and token is not None:
            if RiskLimits.symbol_loss_cooldown_reached(
                exchange=exchange,
                token=token,
            ):
                return (
                    False,
                    "Symbol loss cooldown active. New trades are blocked.",
                )

        if MaxOpenTradesPolicy.reached():
            return (
                False,
                "Maximum open trades reached. New trades are blocked.",
            )

        return True, None

    @classmethod
    def can_open_trade(
        cls,
        *,
        exchange: str | None = None,
        token: str | None = None,
    ) -> bool:
        allowed, _ = cls.evaluate(
            exchange=exchange,
            token=token,
        )
        return allowed
