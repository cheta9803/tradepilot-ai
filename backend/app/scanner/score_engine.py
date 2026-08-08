from app.scanner.models import IndicatorSnapshot
from app.scanner.models import TimeframeSignals


class ScoreEngine:

    BUY = "BUY"

    SELL = "SELL"

    HOLD = "HOLD"

    WATCH = "WATCH"

    MAX_SCORE = 100

    @classmethod
    def calculate(
        cls,
        *,
        indicators: IndicatorSnapshot,
        timeframes: TimeframeSignals,
    ) -> int:

        score = 0

        if indicators.trend == "UP":
            score += 20

        if indicators.ema20_above_ema50:
            score += 10

        if indicators.price_above_ema20:
            score += 10

        if indicators.rsi >= 60:
            score += 10

        elif indicators.rsi >= 50:
            score += 5

        if indicators.macd_bullish:
            score += 10

        if indicators.above_vwap:
            score += 10

        if indicators.supertrend_buy:
            score += 10

        if indicators.breakout:
            score += 10

        if indicators.volume_spike:
            score += 10

        bullish = sum(
            1
            for signal in (
                timeframes.one_minute,
                timeframes.five_minutes,
                timeframes.fifteen_minutes,
                timeframes.one_hour,
            )
            if signal == cls.BUY
        )

        if bullish >= 3:
            score += 10

        return min(
            score,
            cls.MAX_SCORE,
        )