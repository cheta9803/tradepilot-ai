from types import SimpleNamespace

from app.execution.order_service import ExecutionOrderService
from app.orders.enums import OrderStatus


def _trade(
    signal="BUY",
):
    return {
        "exchange": "NSE",
        "token": "123",
        "symbol": "TEST",
        "timeframe": "1m",
        "signal": signal,
        "entry_price": 100.0,
        "stop_loss": 95.0,
        "target": 110.0,
        "quantity": 10,
        "closed_at": None,
        "current_price": 110.0,
        "execution_mode": "PAPER",
    }


def test_buy_exit_creates_sell_order(monkeypatch):

    captured = {}

    def fake_place_order(request):

        captured["request"] = request

        return SimpleNamespace(
            order_id="PAPER-EXIT-1",
            status=OrderStatus.COMPLETE,
            average_price=None,
        )

    monkeypatch.setattr(
        "app.execution.order_service.OrderService.place_order",
        fake_place_order,
    )

    updates = {}

    def fake_update(
        **kwargs,
    ):
        updates.update(kwargs["values"])

    monkeypatch.setattr(
        "app.execution.order_service.TradeLifecycle.update",
        fake_update,
    )

    result = ExecutionOrderService.execute_exit(
        trade=_trade("BUY"),
        exit_price=110.0,
        reason="TARGET",
    )

    assert result is True
    assert captured["request"].transaction_type.value == "SELL"
    assert captured["request"].quantity == 10
    assert updates["state"] == "EXIT"
    assert updates["exit_price"] == 110.0
    assert updates["pnl"] == 100.0
    assert updates["reason"] == "TARGET"


def test_sell_exit_creates_buy_order(monkeypatch):

    captured = {}

    def fake_place_order(request):

        captured["request"] = request

        return SimpleNamespace(
            order_id="PAPER-EXIT-2",
            status=OrderStatus.COMPLETE,
            average_price=None,
        )

    monkeypatch.setattr(
        "app.execution.order_service.OrderService.place_order",
        fake_place_order,
    )

    updates = {}

    def fake_update(
        **kwargs,
    ):
        updates.update(kwargs["values"])

    monkeypatch.setattr(
        "app.execution.order_service.TradeLifecycle.update",
        fake_update,
    )

    result = ExecutionOrderService.execute_exit(
        trade=_trade("SELL"),
        exit_price=90.0,
        reason="STOPLOSS",
    )

    assert result is True
    assert captured["request"].transaction_type.value == "BUY"
    assert captured["request"].quantity == 10
    assert updates["state"] == "EXIT"
    assert updates["exit_price"] == 90.0
    assert updates["pnl"] == 100.0
    assert updates["reason"] == "STOPLOSS"

def test_exit_order_pending_does_not_close_trade(monkeypatch):

    captured = {}

    def fake_place_order(request):
        captured["request"] = request

        return SimpleNamespace(
            order_id="PAPER-EXIT-PENDING",
            status=OrderStatus.PENDING,
            average_price=None,
        )

    monkeypatch.setattr(
        "app.execution.order_service.OrderService.place_order",
        fake_place_order,
    )

    updates = {}

    def fake_update(**kwargs):
        updates.update(kwargs["values"])

    monkeypatch.setattr(
        "app.execution.order_service.TradeLifecycle.update",
        fake_update,
    )

    result = ExecutionOrderService.execute_exit(
        trade=_trade("BUY"),
        exit_price=110.0,
        reason="TARGET",
    )

    assert result is True
    assert captured["request"].transaction_type.value == "SELL"
    assert updates["order_id"] == "PAPER-EXIT-PENDING"
    assert updates["order_status"] == "PENDING"
    assert updates["order_role"] == "EXIT"
    assert "state" not in updates


def test_exit_order_failure_does_not_close_trade(monkeypatch):

    def fake_place_order(request):
        return SimpleNamespace(
            order_id=None,
            status=OrderStatus.FAILED,
            average_price=None,
        )

    monkeypatch.setattr(
        "app.execution.order_service.OrderService.place_order",
        fake_place_order,
    )

    updates = {}

    def fake_update(**kwargs):
        updates.update(kwargs["values"])

    monkeypatch.setattr(
        "app.execution.order_service.TradeLifecycle.update",
        fake_update,
    )

    result = ExecutionOrderService.execute_exit(
        trade=_trade("BUY"),
        exit_price=110.0,
        reason="TARGET",
    )

    assert result is False
    assert updates["order_status"] == "FAILED"
    assert updates["order_role"] == "EXIT"
    assert updates["reason"] == "BROKER_EXIT_ORDER_FAILED"
    assert "state" not in updates