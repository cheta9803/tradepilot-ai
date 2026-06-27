from fastapi import APIRouter

from app.market.schemas import CandleResponse
from app.market.service import MarketService

router = APIRouter(
    prefix="/market",
    tags=["Market"],
)

service = MarketService()


@router.get(
    "/history/{symbol}",
    response_model=list[CandleResponse],
)
async def history(symbol: str):
    return service.get_history(symbol.upper())