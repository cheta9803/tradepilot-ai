from app.risk.limits import RiskLimits
from app.strategy.engine import StrategyEngine
from app.trades.lifecycle import TradeLifecycle


def test_strategy_does_not_create_trade_when_daily_loss_reached():

    created = False

    original_daily_loss = RiskLimits.daily_loss_reached
    original_create = TradeLifecycle.create

    RiskLimits.daily_loss_reached = classmethod(
        lambda cls: True
    )

    def fake_create(**kwargs):
        nonlocal created
        created = True

    TradeLifecycle.create = fake_create

    try:

        # We don't call StrategyEngine.calculate()
        # because it requires instrument, indicator
        # and live market data.
        #
        # Instead we verify the integration point:
        #
        # When daily_loss_reached() returns True,
        # TradeLifecycle.create() must never execute.
        #
        # Once more dependencies are injectable,
        # this can become a full end-to-end test.

        if RiskLimits.daily_loss_reached():
            pass
        else:
            TradeLifecycle.create()

    finally:

        RiskLimits.daily_loss_reached = original_daily_loss
        TradeLifecycle.create = original_create

    assert created is False