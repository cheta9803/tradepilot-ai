from app.candles.models import Candle


class BreakoutDetector:

    LOOKBACK = 20

    @classmethod
    def detect(
        cls,
        candles: list[Candle],
    ) -> tuple[bool, bool]:

        if len(candles) < cls.LOOKBACK:
            return False, False

        recent = candles[-cls.LOOKBACK:]

        current = recent[-1]

        previous = recent[:-1]

        highest = max(
            candle.high
            for candle in previous
        )

        lowest = min(
            candle.low
            for candle in previous
        )

        breakout = (
            current.close > highest
        )

        breakdown = (
            current.close < lowest
        )

        return (
            breakout,
            breakdown,
        )