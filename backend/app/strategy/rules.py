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
        ema50: float | None = None,
    ):
        """Evaluate directional quality, not just indicator majority.

        EMA structure is mandatory when ema50 is available. A trade then
        needs at least 4/5 supportive confirmations. RSI extremes are
        deliberately rejected because an overextended move is a poor fresh
        entry even when the direction is bullish/bearish.
        """
        buy_score = 0
        sell_score = 0
        max_score = 0
        reasons: list[str] = []

        if ema50 is not None:
            max_score += 1
            if ema20 > ema50:
                buy_score += 1
                reasons.append("EMA20 above EMA50")
            elif ema20 < ema50:
                sell_score += 1
                reasons.append("EMA20 below EMA50")

        max_score += 1
        if price > ema20:
            buy_score += 1
            reasons.append("Price above EMA20")
        elif price < ema20:
            sell_score += 1
            reasons.append("Price below EMA20")

        max_score += 1
        if 52 <= rsi < 70:
            buy_score += 1
            reasons.append("RSI supports bullish momentum")
        elif 30 < rsi <= 48:
            sell_score += 1
            reasons.append("RSI supports bearish momentum")
        elif rsi >= 70:
            reasons.append("RSI overbought; fresh BUY rejected")
        elif rsi <= 30:
            reasons.append("RSI oversold; fresh SELL rejected")

        if vwap is not None:
            max_score += 1
            if price > vwap:
                buy_score += 1
                reasons.append("Price above session VWAP")
            elif price < vwap:
                sell_score += 1
                reasons.append("Price below session VWAP")

        max_score += 1
        if macd > signal:
            buy_score += 1
            reasons.append("MACD above Signal")
        elif macd < signal:
            sell_score += 1
            reasons.append("MACD below Signal")

        required = 4 if max_score >= 5 else max(3, max_score - 1)
        winning_score = max(buy_score, sell_score)
        confidence = round((winning_score / max_score) * 100) if max_score else 0

        # Never open a fresh position when momentum is already at an RSI
        # extreme. A bullish indicator majority can otherwise overwhelm the
        # overbought rejection above (e.g. 4/5 bullish confirmations at RSI 72).
        if rsi >= 70 and buy_score > sell_score:
            trade_signal = StrategyRules.HOLD
            reasons.append("BUY rejected because RSI is overbought")
        elif rsi <= 30 and sell_score > buy_score:
            trade_signal = StrategyRules.HOLD
            reasons.append("SELL rejected because RSI is oversold")
        elif buy_score >= required and buy_score > sell_score:
            trade_signal = StrategyRules.BUY
        elif sell_score >= required and sell_score > buy_score:
            trade_signal = StrategyRules.SELL
        else:
            trade_signal = StrategyRules.HOLD

        # Never advertise a high confidence for a HOLD.
        if trade_signal == StrategyRules.HOLD:
            confidence = min(confidence, 50)

        return trade_signal, confidence, reasons
