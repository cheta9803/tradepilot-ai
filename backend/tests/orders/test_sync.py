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