class StrategyRules:

    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

    @staticmethod
    def evaluate(
        ema20: float,
        ema50: float,
        rsi: float,
        price: float,
        vwap: float,
        macd: float,
        signal: float,
    ):

        reasons = []
        score = 0

        if ema20 > ema50:
            reasons.append("EMA20 above EMA50")
            score += 1

        if rsi > 55:
            reasons.append("RSI above 55")
            score += 1

        if price > vwap:
            reasons.append("Price above VWAP")
            score += 1

        if macd > signal:
            reasons.append("MACD above Signal")
            score += 1

        if score == 4:
            trade_signal = StrategyRules.BUY
        elif score == 0:
            trade_signal = StrategyRules.SELL
        else:
            trade_signal = StrategyRules.HOLD

        confidence = {
            4: 90,
            3: 75,
            2: 60,
            1: 40,
            0: 20,
        }[score]

        return trade_signal, confidence, reasons