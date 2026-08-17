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
            raise ValueError("Not enough candles for Supertrend.")

        # Build a Wilder ATR series so the bands evolve candle by candle.
        true_ranges = []
        for i, candle in enumerate(candles):
            if i == 0:
                tr = candle.high - candle.low
            else:
                prev_close = candles[i - 1].close
                tr = max(
                    candle.high - candle.low,
                    abs(candle.high - prev_close),
                    abs(candle.low - prev_close),
                )
            true_ranges.append(float(tr))

        atr_values = [None] * len(candles)
        atr = sum(true_ranges[:period]) / period
        atr_values[period - 1] = atr

        for i in range(period, len(candles)):
            atr = ((atr * (period - 1)) + true_ranges[i]) / period
            atr_values[i] = atr

        final_upper = None
        final_lower = None
        trend = None
        supertrend = None

        for i in range(period - 1, len(candles)):
            candle = candles[i]
            atr = atr_values[i]
            if atr is None:
                continue

            hl2 = (candle.high + candle.low) / 2
            basic_upper = hl2 + multiplier * atr
            basic_lower = hl2 - multiplier * atr

            if final_upper is None:
                final_upper = basic_upper
                final_lower = basic_lower
                trend = "SELL" if candle.close <= hl2 else "BUY"
            else:
                prev_close = candles[i - 1].close
                prev_upper = final_upper
                prev_lower = final_lower

                final_upper = (
                    basic_upper
                    if basic_upper < prev_upper or prev_close > prev_upper
                    else prev_upper
                )
                final_lower = (
                    basic_lower
                    if basic_lower > prev_lower or prev_close < prev_lower
                    else prev_lower
                )

                if trend == "SELL" and candle.close > final_upper:
                    trend = "BUY"
                elif trend == "BUY" and candle.close < final_lower:
                    trend = "SELL"

            supertrend = final_lower if trend == "BUY" else final_upper

        if supertrend is None or trend is None:
            raise ValueError("Unable to calculate Supertrend.")

        return {
            "supertrend": round(supertrend, 2),
            "supertrend_signal": trend,
        }
