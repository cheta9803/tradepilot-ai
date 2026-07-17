class TradeState:

    WAIT = "WAIT"
    READY = "READY"
    BUY = "BUY"
    SELL = "SELL"
    EXIT = "EXIT"

    @classmethod
    def evaluate(
        cls,
        *,
        trend: str,
        signal: str,
        confidence: int,
    ) -> str:

        if confidence < 70:
            return cls.WAIT

        if signal == "BUY":

            if trend == "UPTREND":
                return cls.BUY

            return cls.READY

        if signal == "SELL":

            if trend == "DOWNTREND":
                return cls.SELL

            return cls.READY

        return cls.WAIT