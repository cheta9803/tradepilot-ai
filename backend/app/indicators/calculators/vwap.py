from app.market.models import Candle


class VWAPCalculator:

    @staticmethod
    def calculate(candles: list[Candle]) -> float:
        if not candles:
            raise ValueError("No candles available.")

        cumulative_tp_volume = 0.0
        cumulative_volume = 0

        for candle in candles:
            typical_price = (
                candle.high +
                candle.low +
                candle.close
            ) / 3

            cumulative_tp_volume += (
                typical_price * candle.volume
            )

            cumulative_volume += candle.volume

        if cumulative_volume == 0:
            raise ValueError("Total volume cannot be zero.")

        return round(
            cumulative_tp_volume / cumulative_volume,
            2,
        )