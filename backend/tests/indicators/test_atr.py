from datetime import datetime

from app.indicators.calculators.atr import ATRCalculator
from app.market.models import Candle


def test_atr_returns_float():

    candles = []

    price = 100

    for i in range(30):

        candles.append(
            Candle(
                symbol="TEST",
                timeframe="5m",
                timestamp=datetime.now(),
                open=price,
                high=price + 3,
                low=price - 2,
                close=price + 1,
                volume=1000,
            )
        )

        price += 1

    atr = ATRCalculator.calculate(
        candles,
        period=14,
    )

    assert isinstance(atr, float)
    assert atr > 0