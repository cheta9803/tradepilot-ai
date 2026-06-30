from app.indicators.calculators.ema import EMACalculator
from app.market.models import Candle


class MACDCalculator:

    @staticmethod
    def calculate(
        candles: list[Candle],
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
    ) -> dict:

        if len(candles) < slow_period + signal_period:
            raise ValueError(
                "Not enough candles to calculate MACD."
            )

        fast_ema = EMACalculator.calculate_series(
            candles,
            fast_period,
        )

        slow_ema = EMACalculator.calculate_series(
            candles,
            slow_period,
        )

        offset = len(fast_ema) - len(slow_ema)

        fast_ema = fast_ema[offset:]

        macd_series = [
            round(fast - slow, 2)
            for fast, slow in zip(fast_ema, slow_ema)
        ]

        multiplier = 2 / (signal_period + 1)

        signal = (
            sum(macd_series[:signal_period])
            / signal_period
        )

        signal_series = [signal]

        for value in macd_series[signal_period:]:
            signal = (
                value * multiplier
                + signal * (1 - multiplier)
            )

            signal_series.append(
                round(signal, 2)
            )

        macd = macd_series[-1]
        signal = signal_series[-1]

        histogram = round(
            macd - signal,
            2,
        )

        return {
            "macd": macd,
            "signal": signal,
            "histogram": histogram,
        }