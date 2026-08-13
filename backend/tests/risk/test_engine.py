from app.indicators.cache import IndicatorCache
from app.risk.breakeven import BreakEvenStop
from app.risk.engine import RiskEngine
from app.risk.trailing import TrailingStop
from app.trades.lifecycle import TradeLifecycle


def test_engine_returns_when_indicators_missing():

    trade = {
        "exchange": "NSE",
        "token": "123",
        "timeframe": "1m",
    }

    original_get = IndicatorCache.get

    IndicatorCache.get = classmethod(
        lambda cls, **kwargs: None
    )

    trailing_called = False

    original_trailing = TrailingStop.process

    def fake_trailing(**kwargs):
        nonlocal trailing_called
        trailing_called = True

    TrailingStop.process = fake_trailing

    try:

        RiskEngine.process(
            trade=trade,
            ltp=100.0,
        )

    finally:

        IndicatorCache.get = original_get
        TrailingStop.process = original_trailing

    assert trailing_called is False


def test_engine_passes_atr_to_trailing():

    trade = {
        "exchange": "NSE",
        "token": "123",
        "timeframe": "1m",
    }

    original_get = IndicatorCache.get

    IndicatorCache.get = classmethod(
        lambda cls, **kwargs: {
            "atr14": 5.25,
        }
    )

    captured = {}

    original_trailing = TrailingStop.process

    def fake_trailing(**kwargs):
        captured.update(kwargs)

        return False

    TrailingStop.process = fake_trailing

    original_be = BreakEvenStop.process
    BreakEvenStop.process = lambda **kwargs: None

    try:

        RiskEngine.process(
            trade=trade,
            ltp=150.0,
        )

    finally:

        IndicatorCache.get = original_get
        TrailingStop.process = original_trailing
        BreakEvenStop.process = original_be

    assert captured["trade"] == trade
    assert captured["ltp"] == 150.0
    assert captured["atr"] == 5.25


def test_engine_calls_all_risk_modules():

    trade = {
        "exchange": "NSE",
        "token": "123",
        "timeframe": "1m",
    }

    original_get = IndicatorCache.get

    IndicatorCache.get = classmethod(
        lambda cls, **kwargs: {
            "atr14": 3.0,
        }
    )

    calls = {
        "trailing": 0,
        "breakeven": 0,
    }

    original_trailing = TrailingStop.process
    original_be = BreakEvenStop.process

    def fake_trailing(**kwargs):

        calls["trailing"] += 1

        return False

    def fake_breakeven(**kwargs):

        calls["breakeven"] += 1

    TrailingStop.process = fake_trailing
    BreakEvenStop.process = fake_breakeven

    try:

        RiskEngine.process(
            trade=trade,
            ltp=101.0,
        )

    finally:

        IndicatorCache.get = original_get
        TrailingStop.process = original_trailing
        BreakEvenStop.process = original_be

    assert calls["trailing"] == 1
    assert calls["breakeven"] == 1


def test_engine_reloads_trade_after_trailing_change():

    trade = {
        "exchange": "NSE",
        "token": "123",
        "timeframe": "1m",
        "state": "BUY_ACTIVE",
        "entry_price": 100.0,
        "stop_loss": 95.0,
        "highest_price": 100.0,
    }

    latest_trade = {
        **trade,
        "stop_loss": 105.0,
        "highest_price": 110.0,
        "trail_started": True,
    }

    original_get = IndicatorCache.get
    original_trailing = TrailingStop.process
    original_trade_get = TradeLifecycle.get
    original_breakeven = BreakEvenStop.process

    IndicatorCache.get = classmethod(
        lambda cls, **kwargs: {
            "atr14": 5.0,
        }
    )

    TrailingStop.process = lambda **kwargs: True

    TradeLifecycle.get = classmethod(
        lambda cls, **kwargs: latest_trade
    )

    captured = {}

    def fake_breakeven(**kwargs):
        captured.update(kwargs)

    BreakEvenStop.process = fake_breakeven

    try:

        RiskEngine.process(
            trade=trade,
            ltp=110.0,
        )

    finally:

        IndicatorCache.get = original_get
        TrailingStop.process = original_trailing
        TradeLifecycle.get = original_trade_get
        BreakEvenStop.process = original_breakeven

    assert captured["trade"] is latest_trade
    assert captured["trade"]["stop_loss"] == 105.0
    assert captured["trade"]["highest_price"] == 110.0
    assert captured["ltp"] == 110.0
    assert captured["atr"] == 5.0