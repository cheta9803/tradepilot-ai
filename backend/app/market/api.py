from fastapi import APIRouter, Query

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