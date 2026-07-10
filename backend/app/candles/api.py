from fastapi import APIRouter, HTTPException

from app.candles.redis_cache import CandleCache
from app.candles.schemas import CandleResponse

router = APIRouter(
    prefix="/candles",
    tags=["Candles"],
)


@router.get(
    "/{exchange}/{token}",
    response_model=CandleResponse,
)
def get_current_candle(
    exchange: str,
    token: str,
):

    candle = CandleCache.get(
        exchange=exchange,
        token=token,
        timeframe="1m",
    )

    if candle is None:
        raise HTTPException(
            status_code=404,
            detail="Candle not found.",
        )

    return candle