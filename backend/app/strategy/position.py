from app.strategy.risk import RiskManager


class PositionSizer:

    @classmethod
    def calculate(
        cls,
        *,
        capital: float,
        entry: float,
        stop_loss: float,
    ) -> dict:

        risk_amount = RiskManager.risk_amount(capital)

        risk_per_share = abs(
            entry - stop_loss
        )

        if risk_per_share <= 0:

            return {
                "quantity": 0,
                "invested": 0.0,
                "risk_amount": risk_amount,
            }

        # Quantity based on maximum acceptable risk
        quantity_by_risk = int(
            risk_amount / risk_per_share
        )

        # Quantity based on available capital
        quantity_by_capital = int(
            capital / entry
        )

        quantity = min(
            quantity_by_risk,
            quantity_by_capital,
        )

        invested = round(
            quantity * entry,
            2,
        )

        return {
            "quantity": quantity,
            "invested": invested,
            "risk_amount": risk_amount,
        }