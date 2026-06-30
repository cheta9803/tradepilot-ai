from fastapi import APIRouter, Query

from app.indicators.schemas import EMAResponse
from app.indicators.schemas import SMAResponse
from app.indicators.schemas import RSIResponse
from app.indicators.schemas import VWAPResponse
from app.indicators.schemas import ATRResponse
from app.indicators.schemas import MACDResponse

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

@router.get(
    "/rsi/{symbol}",
    response_model=RSIResponse,
)
async def rsi(
    symbol: str,
    timeframe: str = Query(default="5m"),
    period: int = Query(default=14, ge=2, le=200),
):
    return service.calculate_rsi(
        symbol=symbol.upper(),
        timeframe=timeframe,
        period=period,
    )

@router.get(
    "/vwap/{symbol}",
    response_model=VWAPResponse,
)
async def vwap(
    symbol: str,
    timeframe: str = Query(default="5m"),
):
    return service.calculate_vwap(
        symbol=symbol.upper(),
        timeframe=timeframe,
    )

@router.get(
    "/atr/{symbol}",
    response_model=ATRResponse,
)
async def atr(
    symbol: str,
    timeframe: str = Query(default="5m"),
    period: int = Query(default=14, ge=2, le=200),
):
    return service.calculate_atr(
        symbol=symbol.upper(),
        timeframe=timeframe,
        period=period,
    )

@router.get(
    "/macd/{symbol}",
    response_model=MACDResponse,
)
async def macd(
    symbol: str,
    timeframe: str = Query(default="5m"),
):
    return service.calculate_macd(
        symbol=symbol.upper(),
        timeframe=timeframe,
    )