from pydantic import BaseModel

from app.orders.enums import (
    OrderType,
    ProductType,
    TransactionType,
)


class PlaceOrderRequest(BaseModel):

    symbol: str

    exchange: str

    token: str

    transaction_type: TransactionType

    order_type: OrderType

    product_type: ProductType

    quantity: int

    price: float = 0

    trigger_price: float | None = None


class OrderResponse(BaseModel):

    success: bool

    order_id: str | None

    status: str

    message: str