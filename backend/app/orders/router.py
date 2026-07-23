from fastapi import APIRouter

from app.orders.schemas import (
    OrderResponse,
    PlaceOrderRequest,
)
from app.orders.service import OrderService

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


@router.post(
    "",
    response_model=OrderResponse,
)
def place_order(
    request: PlaceOrderRequest,
) -> OrderResponse:

    order = OrderService.place_order(request)

    return OrderResponse(
        success=order.status != "FAILED",
        order_id=order.order_id,
        status=order.status.value,
        message=order.message or "",
    )