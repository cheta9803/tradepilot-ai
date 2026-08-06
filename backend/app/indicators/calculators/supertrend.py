from app.indicators.calculators.atr import ATRCalculator


class SupertrendCalculator:

    DEFAULT_PERIOD = 10
    DEFAULT_MULTIPLIER = 3.0

    @classmethod
    def calculate(
        cls,
        candles: list,
        period: int = DEFAULT_PERIOD,
        multiplier: float = DEFAULT_MULTIPLIER,
    ) -> dict:

        if len(candles) < period + 2:
            raise ValueError(
                "Not enough candles for Supertrend."
            )

        atr = ATRCalculator.calculate(
            candles,
            period,
        )

        final_upper = None
        final_lower = None
        supertrend = None
        trend = "BUY"

        for candle in candles[-period:]:

            high = candle.high
            low = candle.low
            close = candle.close

            hl2 = (high + low) / 2

            upper_band = hl2 + (multiplier * atr)
            lower_band = hl2 - (multiplier * atr)

            if final_upper is None:
                final_upper = upper_band
                final_lower = lower_band
                supertrend = lower_band
                continue

            if (
                upper_band < final_upper
                or close > final_upper
            ):
                final_upper = upper_band

            if (
                lower_band > final_lower
                or close < final_lower
            ):
                final_lower = lower_band

            if supertrend == final_upper:

                if close <= final_upper:
                    supertrend = final_upper
                    trend = "SELL"
                else:
                    supertrend = final_lower
                    trend = "BUY"

            else:

                if close >= final_lower:
                    supertrend = final_lower
                    trend = "BUY"
                else:
                    supertrend = final_upper
                    trend = "SELL"

        return {
            "supertrend": round(
                supertrend,
                2,
            ),
            "supertrend_signal": trend,
        }