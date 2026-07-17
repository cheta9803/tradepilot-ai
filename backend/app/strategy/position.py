class PositionSizer:

    DEFAULT_RISK_PERCENT = 1.0

    @classmethod
    def calculate(
        cls,
        *,
        capital: float,
        entry: float,
        stop_loss: float,
        risk_percent: float = DEFAULT_RISK_PERCENT,
    ) -> dict:

        risk_amount = capital * (risk_percent / 100)

        risk_per_share = abs(entry - stop_loss)

        if risk_per_share <= 0:
            quantity = 0
        else:
            quantity = int(risk_amount / risk_per_share)

        invested = round(quantity * entry, 2)

        return {
            "capital": capital,
            "risk_percent": risk_percent,
            "risk_amount": round(risk_amount, 2),
            "risk_per_share": round(risk_per_share, 2),
            "quantity": quantity,
            "invested": invested,
        }