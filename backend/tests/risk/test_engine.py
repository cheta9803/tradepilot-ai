from app.indicators.cache import IndicatorCache
from app.risk.breakeven import BreakEvenStop
from app.risk.engine import RiskEngine
from app.risk.trailing import TrailingStop


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

    TrailingStop.process = lambda **kwargs: calls.__setitem__(
        "trailing",
        calls["trailing"] + 1,
    )

    BreakEvenStop.process = lambda **kwargs: calls.__setitem__(
        "breakeven",
        calls["breakeven"] + 1,
    )

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