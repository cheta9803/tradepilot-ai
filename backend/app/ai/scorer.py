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
            score += 20
            reasons.append("Uptrend")
        else:
            reasons.append("Downtrend")

        #
        # EMA
        #
        if strategy["entry"] > strategy["ema20"]:
            score += 15
            reasons.append("Above EMA20")

        #
        # RSI
        #
        rsi = strategy["rsi14"]

        if 55 <= rsi <= 70:
            score += 15
            reasons.append("Strong RSI")

        elif 45 <= rsi < 55:
            score += 5
            reasons.append("Neutral RSI")

        #
        # MACD
        #
        if strategy["macd"] > strategy["signal_line"]:
            score += 15
            reasons.append("MACD Bullish")

        #
        # VWAP
        #
        vwap = strategy.get("vwap")

        if vwap is not None:

            if strategy["entry"] > vwap:
                score += 15
                reasons.append("Above VWAP")

        #
        # Supertrend
        #
        if strategy["supertrend_signal"] == "BUY":
            score += 15
            reasons.append("Supertrend BUY")
        else:
            score -= 10
            reasons.append("Supertrend SELL")

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
        if score >= 80:
            recommendation = "BUY"

        elif score >= 60:
            recommendation = "WATCH"

        else:
            recommendation = "HOLD"

        return {
            "score": score,
            "confidence": score,
            "recommendation": recommendation,
            "reasons": reasons,
        }