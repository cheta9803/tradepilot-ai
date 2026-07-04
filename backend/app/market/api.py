from fastapi import APIRouter, Query

from app.market.schemas import CandleResponse
from app.market.service import MarketService

from fastapi import HTTPException

from app.auth.dependencies import get_current_active_user
from app.users.models import User
from app.market.schemas import LTPResponse
from app.angel.exceptions import AngelAPIException
from fastapi import Depends

router = APIRouter(
    prefix="/market",
    tags=["Market"],
)

service = MarketService()


@router.get(
    "/history/{symbol}",
    response_model=list[CandleResponse],
)
async def history(
    symbol: str,
    timeframe: str = Query(default="5m"),
    limit: int = Query(default=20, ge=1, le=500),
):
    candles = service.get_history(
        symbol=symbol.upper(),
        timeframe=timeframe,
        limit=limit,
    )

    return [
        CandleResponse(
            symbol=c.symbol,
            timeframe=c.timeframe,
            timestamp=c.timestamp,
            open=c.open,
            high=c.high,
            low=c.low,
            close=c.close,
            volume=c.volume,
        )
        for c in candles
    ]

@router.get(
    "/ltp",
    response_model=LTPResponse,
)
def get_ltp(
    exchange: str,
    symbol: str,
    token: str,
    current_user: User = Depends(get_current_active_user),
):
    try:
        data = service.get_ltp(
            exchange=exchange,
            symbol=symbol,
            token=token,
        )

        return LTPResponse(
            symbol=symbol,
            exchange=exchange,
            token=token,
            ltp=data["ltp"],
        )

    except AngelAPIException as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )