from app.market.models import Candle


class SMACalculator:

    @staticmethod
    def calculate(candles: list[Candle], period: int) -> float:
        if len(candles) < period:
            raise ValueError(
                f"Need at least {period} candles to calculate SMA."
            )

        closes = [c.close for c in candles]

        sma = sum(closes[-period:]) / period

        return sma