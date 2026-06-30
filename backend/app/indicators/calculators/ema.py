from app.market.models import Candle


class EMACalculator:

    @staticmethod
    def calculate_series(
        candles: list[Candle],
        period: int,
    ) -> list[float]:

        if len(candles) < period:
            raise ValueError(
                f"Need at least {period} candles to calculate EMA."
            )

        closes = [c.close for c in candles]

        multiplier = 2 / (period + 1)

        ema = sum(closes[:period]) / period

        ema_values = [ema]

        for close in closes[period:]:
            ema = (close * multiplier) + (ema * (1 - multiplier))
            ema_values.append(round(ema, 2))

        return ema_values

    @classmethod
    def calculate(
        cls,
        candles: list[Candle],
        period: int,
    ) -> float:

        return cls.calculate_series(
            candles,
            period,
        )[-1]