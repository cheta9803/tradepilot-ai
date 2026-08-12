from datetime import datetime

from app.strategy.engine import StrategyEngine
from app.strategy.rules import StrategyRules


def test_master_trade_uses_paper_execution_mode(
    monkeypatch,
):
    monkeypatch.setattr(
        "app.strategy.engine.settings.paper_trading",
        True,
    )

    monkeypatch.setattr(
        "app.strategy.engine.MarketSession.can_enter_trade",
        lambda: True,
    )

    monkeypatch.setattr(
        "app.strategy.engine.InstrumentCache.get_by_token",
        lambda token: type(
            "Instrument",
            (),
            {
                "exchange": "NSE",
                "token": token,
                "symbol": "RELIANCE",
            },
        )(),
    )

    candles = [
        type(
            "Candle",
            (),
            {
                "timestamp": datetime.now(),
            },
        )()
    ]

    monkeypatch.setattr(
        "app.strategy.engine.HistoryCache.get",
        lambda **kwargs: candles,
    )

    monkeypatch.setattr(
        "app.strategy.engine.IndicatorCache.get",
        lambda **kwargs: {
            "candle_timestamp": candles[-1].timestamp.isoformat(),
            "ema20": 101.0,
            "ema50": 100.0,
            "rsi14": 60.0,
            "vwap": 100.0,
            "macd": 1.0,
            "signal": 0.5,
            "atr14": 2.0,
            "supertrend": 101.0,
            "supertrend_signal": "BUY",
        },
    )

    monkeypatch.setattr(
        "app.strategy.engine.LiveCache.get",
        lambda token: {
            "ltp": 101.0,
        },
    )

    monkeypatch.setattr(
        "app.strategy.engine.TrendService.evaluate",
        lambda **kwargs: "UPTREND",
    )

    monkeypatch.setattr(
        "app.strategy.engine.StrategyRules.evaluate",
        lambda **kwargs: (
            StrategyRules.BUY,
            80,
            ["Test BUY signal"],
        ),
    )

    monkeypatch.setattr(
        "app.strategy.engine.PatternCache.get",
        lambda **kwargs: None,
    )

    monkeypatch.setattr(
        "app.strategy.engine.RiskManager.calculate",
        lambda **kwargs: (
            99.0,
            105.0,
        ),
    )

    monkeypatch.setattr(
        "app.strategy.engine.PositionSizer.calculate",
        lambda **kwargs: {
            "quantity": 10,
            "invested": 1010.0,
            "risk_amount": 20.0,
        },
    )

    monkeypatch.setattr(
        "app.strategy.engine.MultiTimeframeStrategy.calculate",
        lambda **kwargs: {
            "trade_ready": True,
            "signal": "BUY",
            "confidence": 80,
            "entry": 101.0,
            "stop_loss": 99.0,
            "target": 105.0,
            "reasons": ["All timeframes aligned"],
        },
    )

    monkeypatch.setattr(
        "app.strategy.engine.PreTradeRiskEngine.can_open_trade",
        lambda: True,
    )

    created = {}

    def fake_create(**kwargs):
        created.update(kwargs)

    monkeypatch.setattr(
        "app.strategy.engine.TradeLifecycle.create",
        fake_create,
    )

    monkeypatch.setattr(
        "app.strategy.engine.TradeCache.get",
        lambda **kwargs: None,
    )

    StrategyEngine.calculate(
        exchange="NSE",
        token="2885",
        timeframe="1m",
    )

    assert created["execution_mode"] == "PAPER"
    assert created["signal"] == "BUY"
    assert created["state"] == "ENTRY_READY"