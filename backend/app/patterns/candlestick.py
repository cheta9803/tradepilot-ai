from app.candles.models import Candle

from app.patterns.models import PatternResult


class CandlestickPatternDetector:

    @classmethod
    def detect(
        cls,
        candles: list[Candle],
    ) -> PatternResult:

        result = PatternResult()

        if len(candles) < 2:
            return result

        previous = candles[-2]
        current = candles[-1]

        previous_body = abs(
            previous.close - previous.open
        )

        current_body = abs(
            current.close - current.open
        )

        previous_bearish = (
            previous.close < previous.open
        )

        previous_bullish = (
            previous.close > previous.open
        )

        current_bearish = (
            current.close < current.open
        )

        current_bullish = (
            current.close > current.open
        )

        #
        # Bullish Engulfing
        #
        if (
            previous_bearish
            and current_bullish
            and current.open <= previous.close
            and current.close >= previous.open
        ):

            result.bullish_engulfing = True

        #
        # Bearish Engulfing
        #
        if (
            previous_bullish
            and current_bearish
            and current.open >= previous.close
            and current.close <= previous.open
        ):

            result.bearish_engulfing = True

        upper_shadow = (
            current.high
            - max(
                current.open,
                current.close,
            )
        )

        lower_shadow = (
            min(
                current.open,
                current.close,
            )
            - current.low
        )

        #
        # Hammer
        #
        if (
            lower_shadow > current_body * 2
            and upper_shadow < current_body
        ):

            result.hammer = True

        #
        # Shooting Star
        #
        if (
            upper_shadow > current_body * 2
            and lower_shadow < current_body
        ):

            result.shooting_star = True

        #
        # Doji
        #
        candle_range = (
            current.high - current.low
        )

        if (
            candle_range > 0
            and current_body <= candle_range * 0.1
        ):

            result.doji = True

        return result