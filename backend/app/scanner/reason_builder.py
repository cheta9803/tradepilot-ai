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

        if indicators.trend == "UP":
            reasons.append("Uptrend")

        elif indicators.trend == "DOWN":
            reasons.append("Downtrend")

        if indicators.ema20_above_ema50:
            reasons.append("EMA20 above EMA50")

        if indicators.price_above_ema20:
            reasons.append("Above EMA20")

        if indicators.rsi >= 60:
            reasons.append("Strong RSI")

        elif indicators.rsi >= 50:
            reasons.append("Neutral RSI")

        elif indicators.rsi > 0:
            reasons.append("Weak RSI")

        if indicators.macd_bullish:
            reasons.append("MACD Bullish")

        elif indicators.rsi > 0:
            reasons.append("MACD Bearish")

        if indicators.above_vwap:
            reasons.append("Above VWAP")

        if indicators.supertrend_buy:
            reasons.append("Supertrend BUY")

        elif indicators.trend != "UNKNOWN":
            reasons.append("Supertrend SELL")

        if indicators.breakout:
            reasons.append("Resistance Breakout")

        if indicators.volume_spike:
            reasons.append("Volume Spike")

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
            reasons.append(
                f"Multi-timeframe confirmation ({bullish}/4)",
            )

        elif bullish == 2:
            reasons.append(
                "Partial multi-timeframe confirmation",
            )

        return reasons