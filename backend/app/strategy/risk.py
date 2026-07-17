class RiskManager:

    RISK_REWARD = 2.0

    @classmethod
    def calculate(
        cls,
        *,
        signal: str,
        entry: float,
        atr: float,
    ) -> tuple[float, float]:

        atr = round(atr, 2)

        if signal == "BUY":
            stop_loss = round(entry - atr, 2)
            target = round(entry + (atr * cls.RISK_REWARD), 2)

        elif signal == "SELL":
            stop_loss = round(entry + atr, 2)
            target = round(entry - (atr * cls.RISK_REWARD), 2)

        else:
            stop_loss = round(entry - atr, 2)
            target = round(entry + (atr * cls.RISK_REWARD), 2)

        return stop_loss, target