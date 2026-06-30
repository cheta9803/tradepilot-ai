from datetime import datetime

from app.indicators.calculators.macd import MACDCalculator
from app.market.models import Candle


def test_macd_returns_values():

    candles = []

    price = 100

    for _ in range(60):

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

    result = MACDCalculator.calculate(
        candles,
    )

    assert "macd" in result
    assert "signal" in result
    assert "histogram" in result