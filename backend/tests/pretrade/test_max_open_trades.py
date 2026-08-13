from app.pretrade.max_open_trades import MaxOpenTradesPolicy
from app.trades.cache import TradeCache
from app.core.config import settings


def test_no_open_trades():
    original = TradeCache.get_all

    TradeCache.get_all = classmethod(lambda cls: [])

    try:
        assert MaxOpenTradesPolicy.reached() is False
    finally:
        TradeCache.get_all = original


def test_limit_not_reached():
    original = TradeCache.get_all

    TradeCache.get_all = classmethod(
        lambda cls: [
            {"state": "BUY_ACTIVE"},
            {"state": "SELL_ACTIVE"},
        ]
    )

    old_limit = settings.max_open_trades
    settings.max_open_trades = 5

    try:
        assert MaxOpenTradesPolicy.reached() is False
    finally:
        settings.max_open_trades = old_limit
        TradeCache.get_all = original


def test_limit_reached():
    original = TradeCache.get_all

    TradeCache.get_all = classmethod(
        lambda cls: [
            {"state": "BUY_ACTIVE"},
            {"state": "SELL_ACTIVE"},
            {"state": "BUY_ACTIVE"},
        ]
    )

    old_limit = settings.max_open_trades
    settings.max_open_trades = 3

    try:
        assert MaxOpenTradesPolicy.reached() is True
    finally:
        settings.max_open_trades = old_limit
        TradeCache.get_all = original


def test_closed_trades_not_counted():
    original = TradeCache.get_all

    TradeCache.get_all = classmethod(
        lambda cls: [
            {"state": "EXIT"},
            {"state": "BUY_ACTIVE"},
            {"state": "EXIT"},
        ]
    )

    old_limit = settings.max_open_trades
    settings.max_open_trades = 2

    try:
        assert MaxOpenTradesPolicy.reached() is False
    finally:
        settings.max_open_trades = old_limit
        TradeCache.get_all = original

def test_cooldown_blocks_new_trade(monkeypatch):

    monkeypatch.setattr(
        "app.pretrade.engine.RiskLimits.daily_loss_reached",
        lambda: False,
    )

    monkeypatch.setattr(
        "app.pretrade.engine.RiskLimits.loss_cooldown_reached",
        lambda: True,
    )

    monkeypatch.setattr(
        "app.pretrade.engine.MaxOpenTradesPolicy.reached",
        lambda: False,
    )

    from app.pretrade.engine import PreTradeRiskEngine

    assert PreTradeRiskEngine.can_open_trade() is False
