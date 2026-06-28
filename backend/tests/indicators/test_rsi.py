from datetime import datetime

from app.indicators.calculators.rsi import RSICalculator
from app.market.models import Candle


def test_rsi_returns_float():
    candles = []

    price = 100

    for i in range(40):
        candles.append(
            Candle(
                symbol="TEST",
                timeframe="5m",
                timestamp=datetime.now(),
                open=price,
                high=price + 1,
                low=price - 1,
                close=price,
                volume=1000,
            )
        )

        if i % 2 == 0:
            price += 2
        else:
            price -= 1

    rsi = RSICalculator.calculate(candles, 14)

    assert isinstance(rsi, float)
    assert 0 <= rsi <= 100