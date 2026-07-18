class TradeState:

    WAIT = "WAIT"

    ENTRY_READY = "ENTRY_READY"

    BUY_ACTIVE = "BUY_ACTIVE"
    SELL_ACTIVE = "SELL_ACTIVE"

    TARGET_HIT = "TARGET_HIT"
    STOPLOSS_HIT = "STOPLOSS_HIT"

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
            return cls.ENTRY_READY

        if signal == "SELL":
            return cls.ENTRY_READY

        return cls.WAIT