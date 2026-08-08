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

        #
        # Multi-timeframe agreement
        #
        bullish = sum(
            1
            for signal in timeframes.values()
            if signal == "BUY"
        )

        if bullish >= 3:

            confidence += 10

        elif bullish == 2:

            confidence += 5

        #
        # Trend strength
        #
        trend_strength = indicators.get(
            "trend_strength",
            0,
        )

        if trend_strength >= 80:

            confidence += 10

        elif trend_strength >= 60:

            confidence += 5

        #
        # Volume quality
        #
        if indicators.get(
            "volume_spike",
        ):

            confidence += 5

        #
        # Market confirmation
        #
        if indicators.get(
            "market_trend",
        ) == indicators.get(
            "trend",
        ):

            confidence += 5

        #
        # Risk Reward
        #
        risk_reward = indicators.get(
            "risk_reward",
            0,
        )

        if risk_reward >= 2:

            confidence += 5

        return min(
            confidence,
            cls.MAX_CONFIDENCE,
        )