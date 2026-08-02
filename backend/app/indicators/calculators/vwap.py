from app.candles.models import Candle


class VWAPCalculator:

    @staticmethod
    def calculate(
        candles: list[Candle],
    ) -> float | None:

        if not candles:
            return None

        cumulative_tp_volume = 0.0
        cumulative_volume = 0

        for candle in candles:

            if candle.volume <= 0:
                continue

            typical_price = (
                candle.high +
                candle.low +
                candle.close
            ) / 3

            cumulative_tp_volume += (
                typical_price *
                candle.volume
            )

            cumulative_volume += (
                candle.volume
            )

        if cumulative_volume == 0:
            return None

        return round(
            cumulative_tp_volume /
            cumulative_volume,
            2,
        )