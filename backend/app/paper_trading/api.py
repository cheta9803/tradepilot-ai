from fastapi import APIRouter
from fastapi import HTTPException

from app.paper_trading.schemas import PaperTradeRequest
from app.paper_trading.service import PaperTradingService

router = APIRouter(
    prefix="/paper-trading",
    tags=["Paper Trading"],
)


@router.post(
    "",
)
def create_trade(
    request: PaperTradeRequest,
):

    try:

        return PaperTradingService.create(
            exchange=request.exchange,
            token=request.token,
            timeframe=request.timeframe,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )