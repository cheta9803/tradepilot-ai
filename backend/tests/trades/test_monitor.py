from unittest.mock import patch

from app.trades.monitor import TradeMonitor


def test_monitor_does_not_close_trade_at_target():

    trade = {
        "exchange": "NSE",
        "token": "TEST-TOKEN",
        "symbol": "TEST",
        "timeframe": "1m",
        "state": "BUY_ACTIVE",
        "signal": "BUY",
        "entry_price": 100.0,
        "stop_loss": 95.0,
        "target": 110.0,
        "quantity": 10,
        "current_price": 100.0,
        "pnl": 0.0,
        "exit_price": None,
        "reason": None,
        "closed_at": None,
        "updated_at": None,
        "execution_mode": "PAPER",
    }

    live = {
        "ltp": 110.0,
    }

    with patch(
        "app.trades.monitor.TradeCache.get",
        return_value=trade,
    ), patch(
        "app.trades.monitor.LiveCache.get",
        return_value=live,
    ), patch(
        "app.trades.monitor.TradeCache.save",
    ) as save:

        TradeMonitor.update(
            exchange="NSE",
            token="TEST-TOKEN",
            timeframe="1m",
        )

    updated_trade = save.call_args.kwargs["trade"]

    assert updated_trade.state == "BUY_ACTIVE"
    assert updated_trade.exit_price is None
    assert updated_trade.reason is None
    assert updated_trade.closed_at is None
    assert updated_trade.current_price == 110.0
    assert updated_trade.pnl == 100.0


def test_monitor_does_not_close_trade_at_stoploss():

    trade = {
        "exchange": "NSE",
        "token": "TEST-TOKEN",
        "symbol": "TEST",
        "timeframe": "1m",
        "state": "BUY_ACTIVE",
        "signal": "BUY",
        "entry_price": 100.0,
        "stop_loss": 95.0,
        "target": 110.0,
        "quantity": 10,
        "current_price": 100.0,
        "pnl": 0.0,
        "exit_price": None,
        "reason": None,
        "closed_at": None,
        "updated_at": None,
        "execution_mode": "PAPER",
    }

    live = {
        "ltp": 95.0,
    }

    with patch(
        "app.trades.monitor.TradeCache.get",
        return_value=trade,
    ), patch(
        "app.trades.monitor.LiveCache.get",
        return_value=live,
    ), patch(
        "app.trades.monitor.TradeCache.save",
    ) as save:

        TradeMonitor.update(
            exchange="NSE",
            token="TEST-TOKEN",
            timeframe="1m",
        )

    updated_trade = save.call_args.kwargs["trade"]

    assert updated_trade.state == "BUY_ACTIVE"
    assert updated_trade.exit_price is None
    assert updated_trade.reason is None
    assert updated_trade.closed_at is None
    assert updated_trade.current_price == 95.0
    assert updated_trade.pnl == -50.0