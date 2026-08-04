from app.orders.enums import (
    OrderType,
    ProductType,
    TransactionType,
)
from app.orders.schemas import PlaceOrderRequest
from app.orders.service import OrderService
from app.trades.lifecycle import TradeLifecycle


class ExecutionOrderService:

    @classmethod
    def execute_entry(
        cls,
        trade: dict,
    ) -> bool:

        request = PlaceOrderRequest(
            symbol=trade["symbol"],
            exchange=trade["exchange"],
            token=trade["token"],
            transaction_type=(
                TransactionType.BUY
                if trade["signal"] == "BUY"
                else TransactionType.SELL
            ),
            order_type=OrderType.MARKET,
            product_type=ProductType.INTRADAY,
            quantity=trade["quantity"],
            price=0,
        )

        order = OrderService.place_order(request)

        status = order.status.value.upper()

        values = {
            "order_id": order.order_id,
            "order_status": status,
            "broker": "ANGELONE",
        }

        #
        # Market order filled immediately.
        #
        if status == "COMPLETE":

            values["state"] = (
                "BUY_ACTIVE"
                if trade["signal"] == "BUY"
                else "SELL_ACTIVE"
            )

            TradeLifecycle.update(
                exchange=trade["exchange"],
                token=trade["token"],
                timeframe=trade["timeframe"],
                values=values,
            )

            return True

        #
        # Waiting for exchange.
        #
        if status == "PENDING":

            TradeLifecycle.update(
                exchange=trade["exchange"],
                token=trade["token"],
                timeframe=trade["timeframe"],
                values=values,
            )

            return True

        #
        # Broker rejected immediately.
        #
        values["state"] = "ENTRY_FAILED"

        TradeLifecycle.update(
            exchange=trade["exchange"],
            token=trade["token"],
            timeframe=trade["timeframe"],
            values=values,
        )

        return False