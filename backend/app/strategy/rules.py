class StrategyRules:

    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

    @staticmethod
    def evaluate(
        ema20: float,
        rsi: float,
        price: float,
        vwap: float | None,
        macd: float,
        signal: float,
    ):

        buy_score = 0
        sell_score = 0

        max_score = 3

        reasons: list[str] = []

        # EMA
        if price > ema20:

            buy_score += 1

            reasons.append(
                "Price above EMA20",
            )

        elif price < ema20:

            sell_score += 1

            reasons.append(
                "Price below EMA20",
            )

        # RSI
        if rsi > 55:

            buy_score += 1

            reasons.append(
                "RSI above 55",
            )

        elif rsi < 45:

            sell_score += 1

            reasons.append(
                "RSI below 45",
            )

        # VWAP (optional)
        if vwap is not None:

            max_score += 1

            if price > vwap:

                buy_score += 1

                reasons.append(
                    "Price above VWAP",
                )

            elif price < vwap:

                sell_score += 1

                reasons.append(
                    "Price below VWAP",
                )

        # MACD
        if macd > signal:

            buy_score += 1

            reasons.append(
                "MACD above Signal",
            )

        elif macd < signal:

            sell_score += 1

            reasons.append(
                "MACD below Signal",
            )

        confidence = round(
            (
                max(
                    buy_score,
                    sell_score,
                )
                / max_score
            )
            * 100,
        )

        if buy_score >= 3:

            trade_signal = StrategyRules.BUY

        elif sell_score >= 3:

            trade_signal = StrategyRules.SELL

        else:

            trade_signal = StrategyRules.HOLD

        return (
            trade_signal,
            confidence,
            reasons,
        )