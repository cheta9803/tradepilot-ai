from app.risk.breakeven import BreakEvenStop
from app.trades.lifecycle import TradeLifecycle


def test_buy_moves_stop_to_entry():

    trade = {
        "exchange": "NSE",
        "token": "123",
        "timeframe": "1m",
        "state": "BUY_ACTIVE",
        "entry_price": 100.0,
        "stop_loss": 95.0,
        "breakeven_done": False,
    }

    updates = {}

    original = TradeLifecycle.update

    def fake_update(**kwargs):
        updates.update(kwargs["values"])

    TradeLifecycle.update = fake_update

    try:

        BreakEvenStop.process(
            trade=trade,
            ltp=106.0,
            atr=5.0,
        )

    finally:

        TradeLifecycle.update = original

    assert updates["stop_loss"] == 100.0
    assert updates["breakeven_done"] is True


def test_sell_moves_stop_to_entry():

    trade = {
        "exchange": "NSE",
        "token": "123",
        "timeframe": "1m",
        "state": "SELL_ACTIVE",
        "entry_price": 100.0,
        "stop_loss": 105.0,
        "breakeven_done": False,
    }

    updates = {}

    original = TradeLifecycle.update

    def fake_update(**kwargs):
        updates.update(kwargs["values"])

    TradeLifecycle.update = fake_update

    try:

        BreakEvenStop.process(
            trade=trade,
            ltp=94.0,
            atr=5.0,
        )

    finally:

        TradeLifecycle.update = original

    assert updates["stop_loss"] == 100.0
    assert updates["breakeven_done"] is True


def test_buy_does_not_trigger_before_target():

    trade = {
        "exchange": "NSE",
        "token": "123",
        "timeframe": "1m",
        "state": "BUY_ACTIVE",
        "entry_price": 100.0,
        "stop_loss": 95.0,
        "breakeven_done": False,
    }

    updates = {}

    original = TradeLifecycle.update

    def fake_update(**kwargs):
        updates.update(kwargs["values"])

    TradeLifecycle.update = fake_update

    try:

        BreakEvenStop.process(
            trade=trade,
            ltp=104.0,
            atr=5.0,
        )

    finally:

        TradeLifecycle.update = original

    assert updates == {}


def test_sell_does_not_trigger_before_target():

    trade = {
        "exchange": "NSE",
        "token": "123",
        "timeframe": "1m",
        "state": "SELL_ACTIVE",
        "entry_price": 100.0,
        "stop_loss": 105.0,
        "breakeven_done": False,
    }

    updates = {}

    original = TradeLifecycle.update

    def fake_update(**kwargs):
        updates.update(kwargs["values"])

    TradeLifecycle.update = fake_update

    try:

        BreakEvenStop.process(
            trade=trade,
            ltp=96.0,
            atr=5.0,
        )

    finally:

        TradeLifecycle.update = original

    assert updates == {}


def test_does_not_execute_twice():

    trade = {
        "exchange": "NSE",
        "token": "123",
        "timeframe": "1m",
        "state": "BUY_ACTIVE",
        "entry_price": 100.0,
        "stop_loss": 95.0,
        "breakeven_done": True,
    }

    updates = {}

    original = TradeLifecycle.update

    def fake_update(**kwargs):
        updates.update(kwargs["values"])

    TradeLifecycle.update = fake_update

    try:

        BreakEvenStop.process(
            trade=trade,
            ltp=110.0,
            atr=5.0,
        )

    finally:

        TradeLifecycle.update = original

    assert updates == {}