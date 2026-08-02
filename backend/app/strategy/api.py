from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Query

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
    timeframe: str = Query(
        default="1m",
    ),
):

    try:

        return service.analyze(
            symbol=symbol.upper(),
            timeframe=timeframe,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc