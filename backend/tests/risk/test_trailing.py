from app.risk.trailing import TrailingStop


def test_buy_trailing_moves_stop():

    trade = {
        "exchange": "NSE",
        "token": "123",
        "timeframe": "1m",
        "state": "BUY_ACTIVE",
        "entry_price": 100.0,
        "highest_price": 100.0,
        "stop_loss": 95.0,
    }

    updates = {}

    def fake_update(**kwargs):
        updates.update(kwargs["values"])

    from app.trades.lifecycle import TradeLifecycle

    original = TradeLifecycle.update
    TradeLifecycle.update = fake_update

    try:

        TrailingStop._process_buy(
            trade=trade,
            ltp=110.0,
            atr=2.0,
        )

    finally:

        TradeLifecycle.update = original

    assert updates["highest_price"] == 110.0
    assert updates["trail_started"] is True
    assert updates["stop_loss"] > 95.0


def test_buy_trailing_never_moves_backward():

    trade = {
        "exchange": "NSE",
        "token": "123",
        "timeframe": "1m",
        "state": "BUY_ACTIVE",
        "entry_price": 100.0,
        "highest_price": 110.0,
        "stop_loss": 108.0,
    }

    updates = {}

    def fake_update(**kwargs):
        updates.update(kwargs["values"])

    from app.trades.lifecycle import TradeLifecycle

    original = TradeLifecycle.update
    TradeLifecycle.update = fake_update

    try:

        TrailingStop._process_buy(
            trade=trade,
            ltp=105.0,
            atr=2.0,
        )

    finally:

        TradeLifecycle.update = original

    assert updates == {}


def test_sell_trailing_moves_stop():

    trade = {
        "exchange": "NSE",
        "token": "123",
        "timeframe": "1m",
        "state": "SELL_ACTIVE",
        "entry_price": 100.0,
        "lowest_price": 100.0,
        "stop_loss": 105.0,
    }

    updates = {}

    def fake_update(**kwargs):
        updates.update(kwargs["values"])

    from app.trades.lifecycle import TradeLifecycle

    original = TradeLifecycle.update
    TradeLifecycle.update = fake_update

    try:

        TrailingStop._process_sell(
            trade=trade,
            ltp=90.0,
            atr=2.0,
        )

    finally:

        TradeLifecycle.update = original

    assert updates["lowest_price"] == 90.0
    assert updates["trail_started"] is True
    assert updates["stop_loss"] < 105.0


def test_sell_trailing_never_moves_backward():

    trade = {
        "exchange": "NSE",
        "token": "123",
        "timeframe": "1m",
        "state": "SELL_ACTIVE",
        "entry_price": 100.0,
        "lowest_price": 90.0,
        "stop_loss": 92.0,
    }

    updates = {}

    def fake_update(**kwargs):
        updates.update(kwargs["values"])

    from app.trades.lifecycle import TradeLifecycle

    original = TradeLifecycle.update
    TradeLifecycle.update = fake_update

    try:

        TrailingStop._process_sell(
            trade=trade,
            ltp=95.0,
            atr=2.0,
        )

    finally:

        TradeLifecycle.update = original

    assert updates == {}

def test_buy_trailing_waits_for_meaningful_profit_move(monkeypatch):

    trade = {
        "exchange": "NSE",
        "token": "123",
        "timeframe": "1m",
        "state": "BUY_ACTIVE",
        "entry_price": 100.0,
        "highest_price": 100.0,
        "stop_loss": 95.0,
    }

    updates = {}

    def fake_update(**kwargs):
        updates.update(kwargs["values"])

    monkeypatch.setattr(
        "app.risk.trailing.TradeLifecycle.update",
        fake_update,
    )

    from app.core.config import settings

    original = settings.trailing_start_atr_multiplier
    settings.trailing_start_atr_multiplier = 1.5

    try:
        from app.risk.trailing import TrailingStop

        assert (
            TrailingStop._process_buy(
                trade=trade,
                ltp=102.0,
                atr=2.0,
            )
            is False
        )
    finally:
        settings.trailing_start_atr_multiplier = original

    assert updates == {}


def test_sell_trailing_waits_for_meaningful_profit_move(monkeypatch):

    trade = {
        "exchange": "NSE",
        "token": "123",
        "timeframe": "1m",
        "state": "SELL_ACTIVE",
        "entry_price": 100.0,
        "lowest_price": 100.0,
        "stop_loss": 105.0,
    }

    updates = {}

    def fake_update(**kwargs):
        updates.update(kwargs["values"])

    monkeypatch.setattr(
        "app.risk.trailing.TradeLifecycle.update",
        fake_update,
    )

    from app.core.config import settings

    original = settings.trailing_start_atr_multiplier
    settings.trailing_start_atr_multiplier = 1.5

    try:
        from app.risk.trailing import TrailingStop

        assert (
            TrailingStop._process_sell(
                trade=trade,
                ltp=98.0,
                atr=2.0,
            )
            is False
        )
    finally:
        settings.trailing_start_atr_multiplier = original

    assert updates == {}
