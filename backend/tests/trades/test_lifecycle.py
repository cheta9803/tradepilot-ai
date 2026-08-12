from app.trades.lifecycle import TradeLifecycle


def test_exit_transition_persists_trade_history(monkeypatch):

    trade = {
        "exchange": "NSE",
        "token": "123",
        "symbol": "TEST",
        "timeframe": "1m",
        "state": "BUY_ACTIVE",
        "signal": "BUY",
        "entry_price": 100.0,
        "stop_loss": 95.0,
        "target": 110.0,
        "quantity": 10,
        "opened_at": "2026-08-12T12:00:00",
        "closed_at": None,
        "exit_price": 110.0,
        "pnl": 100.0,
        "current_price": 110.0,
        "reason": "TARGET",
        "order_id": "PAPER-TEST-1",
        "execution_mode": "PAPER",
    }

    saved = {}

    monkeypatch.setattr(
        "app.trades.lifecycle.TradeCache.get",
        lambda **kwargs: trade.copy(),
    )

    def fake_history(trade):
        saved["trade"] = trade.copy()

    monkeypatch.setattr(
        "app.trades.lifecycle.TradeHistoryRepository.create_from_trade",
        fake_history,
    )

    monkeypatch.setattr(
        "app.trades.lifecycle.redis_client.set",
        lambda *args, **kwargs: None,
    )

    TradeLifecycle.update(
        exchange="NSE",
        token="123",
        timeframe="1m",
        values={
            "state": "EXIT",
            "exit_price": 110.0,
            "pnl": 100.0,
            "reason": "TARGET",
        },
    )

    assert saved["trade"]["state"] == "EXIT"
    assert saved["trade"]["exit_price"] == 110.0
    assert saved["trade"]["pnl"] == 100.0
    assert saved["trade"]["reason"] == "TARGET"
    assert saved["trade"]["closed_at"] is not None