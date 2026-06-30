from fastapi import APIRouter, Query

from app.strategy.schemas import StrategyResponse
from app.strategy.service import StrategyService

router = APIRouter(
    prefix="/strategy",
    tags=["Strategy"],
)

service = StrategyService()


@router.get(
    "/intraday/{symbol}",
    response_model=StrategyResponse,
)
async def intraday(
    symbol: str,
    timeframe: str = Query(default="5m"),
):
    return service.analyze(
        symbol=symbol.upper(),
        timeframe=timeframe,
    )