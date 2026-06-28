from app.market.models import Candle


class RSICalculator:

    @staticmethod
    def calculate(candles: list[Candle], period: int = 14) -> float:
        if len(candles) < period + 1:
            raise ValueError(
                f"Need at least {period + 1} candles to calculate RSI."
            )

        closes = [c.close for c in candles]

        gains = []
        losses = []

        for i in range(1, period + 1):
            change = closes[-period - 1 + i] - closes[-period - 2 + i]

            if change >= 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))

        average_gain = sum(gains) / period
        average_loss = sum(losses) / period

        if average_loss == 0:
            return 100.0

        rs = average_gain / average_loss

        rsi = 100 - (100 / (1 + rs))

        return round(rsi, 2)