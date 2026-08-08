from app.scanner.models import IndicatorSnapshot
from app.scanner.models import TimeframeSignals


class ConfidenceEngine:

    MAX_CONFIDENCE = 100

    @classmethod
    def calculate(
        cls,
        *,
        score: int,
        indicators: IndicatorSnapshot,
        timeframes: TimeframeSignals,
    ) -> int:

        confidence = score

        signals = (
            timeframes.one_minute,
            timeframes.five_minutes,
            timeframes.fifteen_minutes,
            timeframes.one_hour,
        )

        bullish = sum(
            1
            for signal in signals
            if signal == "BUY"
        )

        if bullish >= 3:
            confidence += 10

        elif bullish == 2:
            confidence += 5

        if indicators.trend_strength >= 80:
            confidence += 10

        elif indicators.trend_strength >= 60:
            confidence += 5

        if indicators.volume_spike:
            confidence += 5

        if (
            indicators.market_trend != "UNKNOWN"
            and indicators.market_trend == indicators.trend
        ):
            confidence += 5

        if indicators.risk_reward >= 2:
            confidence += 5

        return min(
            confidence,
            cls.MAX_CONFIDENCE,
        )