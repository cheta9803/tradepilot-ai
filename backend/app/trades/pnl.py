class PnLCalculator:

    @staticmethod
    def calculate(
        *,
        signal: str,
        entry: float,
        current: float,
        quantity: int,
    ) -> float:

        if signal == "BUY":
            return round(
                (current - entry) * quantity,
                2,
            )

        if signal == "SELL":
            return round(
                (entry - current) * quantity,
                2,
            )

        return 0.0