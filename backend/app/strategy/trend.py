class TrendService:

    UPTREND = "UPTREND"
    DOWNTREND = "DOWNTREND"
    SIDEWAYS = "SIDEWAYS"

    @classmethod
    def evaluate(
        cls,
        *,
        ema20: float,
        ema50: float,
    ) -> str:

        if ema20 > ema50:
            return cls.UPTREND

        if ema20 < ema50:
            return cls.DOWNTREND

        return cls.SIDEWAYS