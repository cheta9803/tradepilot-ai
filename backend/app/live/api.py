from fastapi import APIRouter
from fastapi import HTTPException

from app.live.instance import live_manager
from app.live.request import SubscribeRequest
from app.live.schemas import LivePriceResponse
from app.live.service import LiveService

router = APIRouter(
    prefix="/live",
    tags=["Live Market"],
)


@router.post("/subscribe")
def subscribe(
    request: SubscribeRequest,
):

    live_manager.subscribe(
        exchange=request.exchange,
        token=request.token,
    )

    return {
        "message": "Subscribed successfully."
    }


@router.post("/unsubscribe")
def unsubscribe(
    request: SubscribeRequest,
):

    live_manager.unsubscribe(
        exchange=request.exchange,
        token=request.token,
    )

    return {
        "message": "Unsubscribed successfully."
    }


@router.get(
    "/{token}",
    response_model=LivePriceResponse,
)
def get_live_price(
    token: str,
):

    data = LiveService.get(token)

    if data is None:
        raise HTTPException(
            status_code=404,
            detail="Live data not available.",
        )

    return data