from app.scanner.models import ScannerResult

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

        reasons: list[str] = []

        #
        # Trend
        #
        if indicators.get("trend") == "UP":

            score += 20

            reasons.append(
                "Uptrend",
            )

        elif indicators.get("trend") == "DOWN":

            reasons.append(
                "Downtrend",
            )

        #
        # EMA
        #
        if indicators.get("ema20_above_ema50"):

            score += 10

            reasons.append(
                "EMA20 above EMA50",
            )

        #
        # Price above EMA20
        #
        if indicators.get("price_above_ema20"):

            score += 10

            reasons.append(
                "Above EMA20",
            )

        #
        # RSI
        #
        rsi = indicators.get(
            "rsi",
            0,
        )

        if rsi >= 60:

            score += 10

            reasons.append(
                "Strong RSI",
            )

        elif rsi >= 50:

            score += 5

            reasons.append(
                "Neutral RSI",
            )

        #
        # MACD
        #
        if indicators.get("macd_bullish"):

            score += 10

            reasons.append(
                "MACD Bullish",
            )

        #
        # VWAP
        #
        if indicators.get("above_vwap"):

            score += 10

            reasons.append(
                "Above VWAP",
            )

        #
        # Supertrend
        #
        if indicators.get("supertrend_buy"):

            score += 10

            reasons.append(
                "Supertrend BUY",
            )

        #
        # Breakout
        #
        if indicators.get("breakout"):

            score += 10

            reasons.append(
                "Resistance Breakout",
            )

        #
        # Volume
        #
        if indicators.get("volume_spike"):

            score += 10

            reasons.append(
                "Volume Spike",
            )

        #
        # Multi Timeframe
        #
        bullish = sum(
            1
            for signal in timeframes.values()
            if signal == cls.BUY
        )

        if bullish >= 3:

            score += 10

            reasons.append(
                "Multi-timeframe confirmation",
            )

        score = min(
            score,
            cls.MAX_SCORE,
        )

        if score >= 85:

            recommendation = cls.BUY

        elif score >= 65:

            recommendation = cls.WATCH

        else:

            recommendation = cls.HOLD

        return ScannerResult(
            exchange="",
            symbol="",
            token="",
            score=score,
            confidence=score,
            recommendation=recommendation,
            reasons=reasons,
            indicators=indicators,
            timeframes=timeframes,
        )