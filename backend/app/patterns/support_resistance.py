from app.candles.models import Candle


class SupportResistanceDetector:

    LOOKBACK = 20

    @classmethod
    def detect(
        cls,
        candles: list[Candle],
    ) -> tuple[float | None, float | None]:
        """Return prior support/resistance, excluding the trigger candle.

        The old implementation included the current candle. During a
        breakout, that made resistance equal to the breakout candle's own
        high, so the entry-location filter could reject the breakout it had
        just confirmed.
        """
        if len(candles) < cls.LOOKBACK + 1:
            return None, None

        recent = candles[-(cls.LOOKBACK + 1):-1]

        support = min(candle.low for candle in recent)
        resistance = max(candle.high for candle in recent)

        return round(support, 2), round(resistance, 2)
