from datetime import datetime
from uuid import uuid4

from app.angel.client import AngelClient
from app.core.config import settings
from app.core.retry import Retry
from app.orders.enums import OrderStatus
from app.orders.models import Order


class SmartAPIOrderService:

    @classmethod
    def place_order(
        cls,
        order: Order,
    ) -> Order:

        if settings.paper_trading:

            order.order_id = f"PAPER-{uuid4().hex[:12]}"
            order.status = OrderStatus.COMPLETE
            order.message = "Paper trading order executed"
            order.created_at = datetime.now()

            return order

        response = Retry.execute(
            cls._place_order,
            order,
        )

        if response is None:

            order.status = OrderStatus.FAILED
            order.message = "Broker did not return a response."

        elif response.get("status", False):

            order.order_id = response["data"]["orderid"]
            order.status = OrderStatus.PENDING
            order.message = response.get(
                "message",
                "Order submitted",
            )

        else:

            order.status = OrderStatus.FAILED
            order.message = response.get(
                "message",
                "Order placement failed",
            )

        order.created_at = datetime.now()

        return order

    @classmethod
    def _place_order(
        cls,
        order: Order,
    ) -> dict | None:

        payload = {
            "variety": "NORMAL",
            "tradingsymbol": order.symbol,
            "symboltoken": order.token,
            "transactiontype": order.transaction_type.value,
            "exchange": order.exchange,
            "ordertype": order.order_type.value,
            "producttype": order.product_type.value,
            "duration": "DAY",
            "price": str(order.price),
            "squareoff": "0",
            "stoploss": "0",
            "quantity": str(order.quantity),
        }

        if order.trigger_price is not None:
            payload["triggerprice"] = str(
                order.trigger_price
            )

        smart_api = AngelClient.get_client()

        return smart_api.placeOrderFullResponse(
            payload
        )