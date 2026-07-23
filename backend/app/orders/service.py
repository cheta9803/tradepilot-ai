from datetime import datetime

from app.orders.enums import OrderStatus
from app.orders.models import Order
from app.orders.schemas import PlaceOrderRequest
from app.orders.smartapi import SmartAPIOrderService


class OrderService:

    @classmethod
    def place_order(
        cls,
        request: PlaceOrderRequest,
    ) -> Order:

        order = Order(
            order_id=None,
            symbol=request.symbol,
            exchange=request.exchange,
            token=request.token,
            transaction_type=request.transaction_type,
            order_type=request.order_type,
            product_type=request.product_type,
            quantity=request.quantity,
            price=request.price,
            trigger_price=request.trigger_price,
            status=OrderStatus.PENDING,
            message=None,
            created_at=datetime.now(),
        )

        return SmartAPIOrderService.place_order(order)