from app.scanner.models import IndicatorSnapshot
from app.scanner.models import TimeframeSignals


class ReasonBuilder:

    @staticmethod
    def build(
        *,
        indicators: IndicatorSnapshot,
        timeframes: TimeframeSignals,
    ) -> list[str]:

        reasons: list[str] = []

        #
        # Trend
        #
        if indicators.get("trend") == "UP":
            reasons.append("Uptrend")
        elif indicators.get("trend") == "DOWN":
            reasons.append("Downtrend")

        #
        # EMA
        #
        if indicators.get("ema20_above_ema50"):
            reasons.append("EMA20 above EMA50")

        if indicators.get("price_above_ema20"):
            reasons.append("Above EMA20")

        #
        # RSI
        #
        rsi = indicators.get("rsi", 0)

        if rsi >= 60:
            reasons.append("Strong RSI")
        elif rsi >= 50:
            reasons.append("Neutral RSI")

        #
        # MACD
        #
        if indicators.get("macd_bullish"):
            reasons.append("MACD Bullish")

        #
        # VWAP
        #
        if indicators.get("above_vwap"):
            reasons.append("Above VWAP")

        #
        # Supertrend
        #
        if indicators.get("supertrend_buy"):
            reasons.append("Supertrend BUY")

        #
        # Breakout
        #
        if indicators.get("breakout"):
            reasons.append("Resistance Breakout")

        #
        # Volume
        #
        if indicators.get("volume_spike"):
            reasons.append("Volume Spike")

        #
        # Multi Timeframe
        #
        bullish = sum(
            1
            for signal in timeframes.values()
            if signal == "BUY"
        )

        if bullish >= 3:
            reasons.append(
                f"Multi-timeframe confirmation ({bullish})",
            )

        return reasons