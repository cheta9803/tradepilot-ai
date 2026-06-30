from app.market.models import Candle


class ATRCalculator:

    @staticmethod
    def calculate(
        candles: list[Candle],
        period: int = 14,
    ) -> float:

        if len(candles) < period + 1:
            raise ValueError(
                f"Need at least {period + 1} candles."
            )

        true_ranges = []

        for i in range(1, len(candles)):
            current = candles[i]
            previous = candles[i - 1]

            tr = max(
                current.high - current.low,
                abs(current.high - previous.close),
                abs(current.low - previous.close),
            )

            true_ranges.append(tr)

        atr = sum(true_ranges[-period:]) / period

        return round(atr, 2)