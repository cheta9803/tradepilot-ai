from app.ai.models import AIScore


class AIScorer:

    @classmethod
    def calculate(
        cls,
        *,
        strategy: dict,
        patterns: dict | None,
    ) -> dict:

        score = 0
        reasons = []

        #
        # Trend
        #
        if strategy["trend"] == "UPTREND":
            score += 12
            reasons.append("Uptrend")
        else:
            score -= 8
            reasons.append("Downtrend")

        #
        # EMA
        #
        if strategy["entry"] > strategy["ema20"]:
            score += 10
            reasons.append("Above EMA20")

        #
        # RSI
        #
        rsi = strategy["rsi14"]

        if 55 <= rsi <= 70:
            score += 12
            reasons.append("Strong RSI")

        elif 45 <= rsi < 55:
            score += 3
            reasons.append("Neutral RSI")

        #
        # MACD
        #
        if strategy["macd"] > strategy["signal_line"]:
            score += 10
            reasons.append("MACD Bullish")

        #
        # VWAP
        #
        vwap = strategy.get("vwap")

        if vwap is not None:

            if strategy["entry"] > vwap:
                score += 8
                reasons.append("Above VWAP")

        #
        # Supertrend
        #
        if strategy["supertrend_signal"] == "BUY":
            score += 14
            reasons.append("Supertrend BUY")
        elif strategy["supertrend_signal"] == "SELL":
            score -= 6
            reasons.append("Supertrend SELL")
        else:
            score -= 2
            reasons.append("Supertrend Neutral")

        #
        # Candlestick Patterns
        #
        if patterns:

            if patterns.get("bullish_engulfing"):
                score += 10
                reasons.append("Bullish Engulfing")

            if patterns.get("morning_star"):
                score += 10
                reasons.append("Morning Star")

            if patterns.get("hammer"):
                score += 8
                reasons.append("Hammer")

            if patterns.get("breakout"):
                score += 10
                reasons.append("Resistance Breakout")

            if patterns.get("bearish_engulfing"):
                score -= 15

            if patterns.get("evening_star"):
                score -= 15

            if patterns.get("shooting_star"):
                score -= 10

            if patterns.get("breakdown"):
                score -= 15

        #
        # Clamp score
        #
        score = max(0, min(score, 100))

        #
        # Recommendation
        #
        if score >= 55:
            recommendation = "BUY"

        elif score >= 25:
            recommendation = "WATCH"

        elif score >= 10:
            recommendation = "HOLD"

        else:
            recommendation = "NO SIGNAL"

        return {
            "score": score,
            "confidence": score,
            "recommendation": recommendation,
            "reasons": reasons,
        }