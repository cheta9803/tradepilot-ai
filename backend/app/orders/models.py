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

    # -------------------------------------------------
    # Broker Identity
    # -------------------------------------------------

    order_id: str | None

    exchange_order_id: str | None = None

    # -------------------------------------------------
    # Instrument
    # -------------------------------------------------

    symbol: str = ""

    exchange: str = ""

    token: str = ""

    # -------------------------------------------------
    # Order Details
    # -------------------------------------------------

    transaction_type: TransactionType | None = None

    order_type: OrderType | None = None

    product_type: ProductType | None = None

    quantity: int = 0

    price: float = 0.0

    trigger_price: float | None = None

    # -------------------------------------------------
    # Execution
    # -------------------------------------------------

    average_price: float | None = None

    filled_quantity: int = 0

    pending_quantity: int = 0

    status: OrderStatus = OrderStatus.PENDING

    message: str | None = None

    # -------------------------------------------------
    # Audit
    # -------------------------------------------------

    created_at: datetime = datetime.now()

    updated_at: datetime | None = None