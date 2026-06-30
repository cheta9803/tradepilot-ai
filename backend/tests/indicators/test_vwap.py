from datetime import datetime

from app.indicators.calculators.vwap import VWAPCalculator
from app.market.models import Candle


def test_vwap_returns_float():
    candles = []

    price = 100

    for _ in range(20):
        candles.append(
            Candle(
                symbol="TEST",
                timeframe="5m",
                timestamp=datetime.now(),
                open=price,
                high=price + 2,
                low=price - 2,
                close=price + 1,
                volume=1000,
            )
        )

        price += 1

    value = VWAPCalculator.calculate(candles)

    assert isinstance(value, float)