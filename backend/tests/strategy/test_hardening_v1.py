from datetime import datetime, timedelta

from app.core.config import settings
from app.indicators.calculators.vwap import VWAPCalculator
from app.indicators.calculators.supertrend import SupertrendCalculator
from app.strategy.rules import StrategyRules
from app.candles.models import Candle


def candle(ts, price, volume=100):
    return Candle(
        exchange="NSE",
        symbol="TEST",
        token="1",
        timeframe="5m",
        timestamp=ts,
        open=price,
        high=price + 1,
        low=price - 1,
        close=price,
        volume=volume,
    )


def test_vwap_uses_latest_session_only():
    day1 = datetime(2026, 8, 14, 9, 15)
    day2 = datetime(2026, 8, 17, 9, 15)
    candles = [candle(day1, 100, 1000), candle(day2, 200, 1000)]
    assert VWAPCalculator.calculate(candles) == 200.0


def test_strategy_rejects_overbought_buy():
    signal, confidence, reasons = StrategyRules.evaluate(
        ema20=100, ema50=99, price=105, vwap=100,
        macd=2, signal=1, rsi=72,
    )
    assert signal == StrategyRules.HOLD
    assert confidence <= 50
    assert any("overbought" in r.lower() for r in reasons)


def test_strategy_requires_strong_majority():
    signal, confidence, _ = StrategyRules.evaluate(
        ema20=100, ema50=99, price=101, vwap=100,
        macd=0.5, signal=1, rsi=50,
    )
    assert signal == StrategyRules.HOLD
    assert confidence <= 50


def test_supertrend_returns_valid_direction():
    start = datetime(2026, 8, 17, 9, 15)
    candles = []
    price = 100.0
    for i in range(30):
        price += 0.5
        candles.append(candle(start + timedelta(minutes=5 * i), price))
    result = SupertrendCalculator.calculate(candles)
    assert result["supertrend_signal"] in {"BUY", "SELL"}
    assert isinstance(result["supertrend"], float)


def test_support_resistance_excludes_current_trigger_candle():
    from app.patterns.support_resistance import SupportResistanceDetector

    start = datetime(2026, 8, 17, 9, 15)
    candles = []
    for i in range(21):
        price = 100 + i * 0.1
        candles.append(candle(start + timedelta(minutes=5 * i), price))

    # Make the current candle a large breakout. Its high must not become the
    # resistance used to judge the breakout's entry location.
    candles[-1].high = 150
    candles[-1].close = 149

    support, resistance = SupportResistanceDetector.detect(candles)
    assert resistance < 150
    assert resistance == round(max(c.high for c in candles[-21:-1]), 2)


def test_multi_timeframe_allows_strong_weighted_alignment():
    from app.strategy.multi_timeframe import MultiTimeframeStrategy

    assert MultiTimeframeStrategy.MIN_CONFIDENCE == 70
    assert MultiTimeframeStrategy.MIN_CONFIDENCE_BY_TIMEFRAME == {
        "15m": 65,
        "5m": 65,
        "1m": 70,
    }
