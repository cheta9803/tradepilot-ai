from app.candles.models import Candle


class SupportResistanceDetector:

    LOOKBACK = 20

    @classmethod
    def detect(
        cls,
        candles: list[Candle],
    ) -> tuple[float | None, float | None]:

        if len(candles) < cls.LOOKBACK:
            return None, None

        recent = candles[-cls.LOOKBACK :]

        support = min(
            candle.low
            for candle in recent
        )

        resistance = max(
            candle.high
            for candle in recent
        )

        return (
            round(
                support,
                2,
            ),
            round(
                resistance,
                2,
            ),
        )