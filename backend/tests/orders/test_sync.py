from unittest.mock import patch

from app.orders.sync import OrderSyncService


def test_sync_trade_failed_order_marks_entry_failed():

    trade = {
        "exchange": "NSE",
        "token": "2885",
        "timeframe": "5m",
        "signal": "BUY",
        "state": "ENTRY_READY",
    }

    order = {
        "status": "FAILED",
        "average_price": None,
    }

    with patch(
        "app.orders.sync.TradeLifecycle.update"
    ) as update:

        OrderSyncService.sync_trade(
            trade=trade,
            order=order,
        )

        update.assert_called_once()

        values = update.call_args.kwargs["values"]

        assert values["order_status"] == "FAILED"
        assert values["state"] == "ENTRY_FAILED"
        assert values["reason"] == "Broker Order Failed"
        assert values["closed_at"] is not None

def test_exit_order_pending_keeps_position_active(monkeypatch):

    trade = {
        "exchange": "NSE",
        "token": "123",
        "timeframe": "1m",
        "signal": "BUY",
        "state": "BUY_ACTIVE",
        "entry_price": 100.0,
        "quantity": 10,
        "order_role": "EXIT",
    }

    updates = {}

    monkeypatch.setattr(
        "app.orders.sync.TradeLifecycle.update",
        lambda **kwargs: updates.update(kwargs["values"]),
    )

    OrderSyncService.sync_trade(
        trade=trade,
        order={
            "status": "PENDING",
            "average_price": None,
        },
    )

    assert updates["state"] == "BUY_ACTIVE"
    assert updates["order_status"] == "PENDING"


def test_exit_order_failed_keeps_position_active(monkeypatch):

    trade = {
        "exchange": "NSE",
        "token": "123",
        "timeframe": "1m",
        "signal": "BUY",
        "state": "BUY_ACTIVE",
        "entry_price": 100.0,
        "quantity": 10,
        "order_role": "EXIT",
    }

    updates = {}

    monkeypatch.setattr(
        "app.orders.sync.TradeLifecycle.update",
        lambda **kwargs: updates.update(kwargs["values"]),
    )

    OrderSyncService.sync_trade(
        trade=trade,
        order={
            "status": "FAILED",
            "average_price": None,
        },
    )

    assert updates["state"] == "BUY_ACTIVE"
    assert updates["order_status"] == "FAILED"
    assert updates["reason"] == "BROKER_EXIT_ORDER_FAILED"