from fastapi import APIRouter, Query

from app.indicators.schemas import EMAResponse
from app.indicators.schemas import SMAResponse
from app.indicators.service import IndicatorService

router = APIRouter(
    prefix="/indicators",
    tags=["Indicators"],
)

service = IndicatorService()


@router.get(
    "/ema/{symbol}",
    response_model=EMAResponse,
)
async def ema(
    symbol: str,
    timeframe: str = Query(default="5m"),
    period: int = Query(default=20, ge=2, le=200),
):
    return service.calculate_ema(
        symbol=symbol.upper(),
        timeframe=timeframe,
        period=period,
    )

@router.get(
    "/sma/{symbol}",
    response_model=SMAResponse,
)
async def sma(
    symbol: str,
    timeframe: str = Query(default="5m"),
    period: int = Query(default=20, ge=2, le=200),
):
    return service.calculate_sma(
        symbol=symbol.upper(),
        timeframe=timeframe,
        period=period,
    )