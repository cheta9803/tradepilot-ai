class StrategyRules:

    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

    @staticmethod
    def evaluate(
        ema20: float,
        rsi: float,
        price: float,
        vwap: float,
        macd: float,
        signal: float,
    ):

        buy_score = 0
        sell_score = 0

        reasons = []

        # Price vs EMA20
        if price > ema20:
            buy_score += 1
            reasons.append("Price above EMA20")
        elif price < ema20:
            sell_score += 1
            reasons.append("Price below EMA20")

        # RSI
        if rsi > 55:
            buy_score += 1
            reasons.append("RSI above 55")
        elif rsi < 45:
            sell_score += 1
            reasons.append("RSI below 45")

        # VWAP
        if price > vwap:
            buy_score += 1
            reasons.append("Price above VWAP")
        elif price < vwap:
            sell_score += 1
            reasons.append("Price below VWAP")

        # MACD
        if macd > signal:
            buy_score += 1
            reasons.append("MACD above Signal")
        elif macd < signal:
            sell_score += 1
            reasons.append("MACD below Signal")

        if buy_score == 4:
            trade_signal = StrategyRules.BUY
            confidence = 90

        elif sell_score == 4:
            trade_signal = StrategyRules.SELL
            confidence = 90

        else:
            trade_signal = StrategyRules.HOLD
            confidence = 50

        return trade_signal, confidence, reasons