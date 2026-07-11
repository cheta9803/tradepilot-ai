from datetime import datetime

from fastapi import APIRouter

from app.candles.service import CandleService

router = APIRouter(
    prefix="/candles/test",
    tags=["Candles Test"],
)


@router.post("")
def create_test_candle():

    CandleService.process_tick(
        exchange="NSE",
        symbol="RELIANCE",
        token="2885",
        price=1500.25,
        volume=10,
        timestamp=datetime.now(),
    )

    return {
        "message": "Test candle processed."
    }