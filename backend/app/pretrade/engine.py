from app.pretrade.max_open_trades import MaxOpenTradesPolicy
from app.risk.limits import RiskLimits


class PreTradeRiskEngine:
    """
    Evaluates whether a new trade is allowed.

    This engine performs all account-level checks
    before a trade is created.
    """

    @classmethod
    def can_open_trade(cls) -> bool:

        if RiskLimits.daily_loss_reached():
            print(
                "Daily loss limit reached. "
                "Skipping new trade."
            )
            return False

        if RiskLimits.loss_cooldown_reached():
            print(
                "Consecutive-loss cooldown active. "
                "Skipping new trade."
            )
            return False

        if MaxOpenTradesPolicy.reached():
            print(
                "Maximum open trades reached. "
                "Skipping new trade."
            )
            return False

        return True
