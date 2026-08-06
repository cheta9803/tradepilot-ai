from app.ai.models import AIScore


class AIScorer:

    @classmethod
    def calculate(
        cls,
        *,
        strategy: dict,
        patterns: dict,
    ) -> AIScore:

        score = 50

        reasons = []

        #
        # Trend
        #
        if strategy["trend"] == "UPTREND":

            score += 10

            reasons.append(
                "Uptrend"
            )

        elif strategy["trend"] == "DOWNTREND":

            score -= 10

            reasons.append(
                "Downtrend"
            )

        #
        # EMA
        #
        if strategy["entry"] > strategy["ema20"]:

            score += 10

            reasons.append(
                "Above EMA20"
            )

        #
        # RSI
        #
        if strategy["rsi14"] >= 60:

            score += 10

            reasons.append(
                "Strong RSI"
            )

        elif strategy["rsi14"] <= 40:

            score -= 10

            reasons.append(
                "Weak RSI"
            )

        #
        # MACD
        #
        if strategy["macd"] > strategy["signal_line"]:

            score += 10

            reasons.append(
                "MACD Bullish"
            )

        else:

            score -= 10

            reasons.append(
                "MACD Bearish"
            )

        #
        # Supertrend
        #
        if strategy["supertrend_signal"] == "BUY":

            score += 10

            reasons.append(
                "Supertrend BUY"
            )

        else:

            score -= 10

            reasons.append(
                "Supertrend SELL"
            )

        #
        # Candlestick Patterns
        #
        if patterns:

            if patterns["bullish_engulfing"]:

                score += 10

                reasons.append(
                    "Bullish Engulfing"
                )

            if patterns["bearish_engulfing"]:

                score -= 10

                reasons.append(
                    "Bearish Engulfing"
                )

            if patterns["hammer"]:

                score += 5

                reasons.append(
                    "Hammer"
                )

            if patterns["shooting_star"]:

                score -= 5

                reasons.append(
                    "Shooting Star"
                )

            if patterns["breakout"]:

                score += 10

                reasons.append(
                    "Breakout"
                )

            if patterns["breakdown"]:

                score -= 10

                reasons.append(
                    "Breakdown"
                )

        score = max(
            0,
            min(
                score,
                100,
            ),
        )

        recommendation = "HOLD"

        if score >= 75:

            recommendation = "BUY"

        elif score <= 25:

            recommendation = "SELL"

        return AIScore(
            score=score,
            reasons=reasons,
            recommendation=recommendation,
            confidence=score,
        )