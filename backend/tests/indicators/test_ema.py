from datetime import datetime

from app.indicators.calculators.ema import EMACalculator
from app.market.models import Candle


def test_ema_returns_float():
    candles = []

    price = 100

    for i in range(30):
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

        price += 1

    ema = EMACalculator.calculate(candles, 20)

    assert isinstance(ema, float)