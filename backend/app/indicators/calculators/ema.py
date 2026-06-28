from app.market.models import Candle


class EMACalculator:

    @staticmethod
    def calculate(candles: list[Candle], period: int) -> float:
        if len(candles) < period:
            raise ValueError(
                f"Need at least {period} candles to calculate EMA."
            )

        closes = [c.close for c in candles]

        multiplier = 2 / (period + 1)

        # First EMA starts with SMA
        ema = sum(closes[:period]) / period

        for close in closes[period:]:
            ema = (close * multiplier) + (ema * (1 - multiplier))

        return round(ema, 2)