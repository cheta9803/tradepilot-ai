from fastapi import APIRouter

from app.indicators.engine import IndicatorEngine

router = APIRouter(
    prefix="/indicators/test",
    tags=["Indicator Test"],
)


@router.post(
    "/calculate/{symbol}",
)
async def calculate(
    symbol: str,
    timeframe: str = "1m",
):

    result = IndicatorEngine.calculate(
        symbol=symbol.upper(),
        timeframe=timeframe,
    )

    return {
        "success": True,
        "data": result,
    }