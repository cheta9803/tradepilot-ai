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
            "order_role": "ENTRY",
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
        if status in (
            "PENDING",
            "OPEN",
        ):

            TradeLifecycle.update(
                exchange=trade["exchange"],
                token=trade["token"],
                timeframe=trade["timeframe"],
                values=values,
            )

            return True

        #
        # Broker rejected / failed.
        #
        values.update(
            {
                "state": "ENTRY_FAILED",
                "reason": "BROKER_ORDER_FAILED",
            }
        )

        TradeLifecycle.update(
            exchange=trade["exchange"],
            token=trade["token"],
            timeframe=trade["timeframe"],
            values=values,
        )

        return False

    @classmethod
    def execute_exit(
        cls,
        trade: dict,
        exit_price: float,
        reason: str,
    ) -> bool:

        #
        # Exit direction is opposite to the open position.
        #
        transaction_type = (
            TransactionType.SELL
            if trade["signal"] == "BUY"
            else TransactionType.BUY
        )

        request = PlaceOrderRequest(
            symbol=trade["symbol"],
            exchange=trade["exchange"],
            token=trade["token"],
            transaction_type=transaction_type,
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
            "order_role": "EXIT",
            "reason": reason,
        }

        #
        # Paper trading completes immediately.
        # A live market order may also complete immediately.
        #
        if status == "COMPLETE":

            final_price = (
                order.average_price
                if order.average_price is not None
                else exit_price
            )

            final_price = float(final_price)

            if trade["signal"] == "BUY":
                pnl = (
                    final_price
                    - trade["entry_price"]
                ) * trade["quantity"]
            else:
                pnl = (
                    trade["entry_price"]
                    - final_price
                ) * trade["quantity"]

            values.update(
                {
                    "state": "EXIT",
                    "exit_price": round(final_price, 2),
                    "current_price": round(final_price, 2),
                    "pnl": round(pnl, 2),
                }
            )

            TradeLifecycle.update(
                exchange=trade["exchange"],
                token=trade["token"],
                timeframe=trade["timeframe"],
                values=values,
            )

            return True

        #
        # Exit order is waiting at the broker.
        #
        if status in (
            "PENDING",
            "OPEN",
        ):

            TradeLifecycle.update(
                exchange=trade["exchange"],
                token=trade["token"],
                timeframe=trade["timeframe"],
                values=values,
            )

            return True

        #
        # Exit order failed.
        #
        values.update(
            {
                "reason": "BROKER_EXIT_ORDER_FAILED",
            }
        )

        TradeLifecycle.update(
            exchange=trade["exchange"],
            token=trade["token"],
            timeframe=trade["timeframe"],
            values=values,
        )

        return False