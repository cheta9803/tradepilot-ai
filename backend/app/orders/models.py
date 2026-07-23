from dataclasses import dataclass
from datetime import datetime

from app.orders.enums import (
    OrderStatus,
    OrderType,
    ProductType,
    TransactionType,
)


@dataclass(slots=True)
class Order:

    order_id: str | None

    symbol: str

    exchange: str

    token: str

    transaction_type: TransactionType

    order_type: OrderType

    product_type: ProductType

    quantity: int

    price: float

    trigger_price: float | None

    status: OrderStatus

    message: str | None

    created_at: datetime