from app.strategy.cache import StrategyCache


class TimeframeConfirmation:

    TIMEFRAMES = [
        "1m",
        "5m",
        "15m",
        "1h",
    ]

    @classmethod
    def calculate(
        cls,
        *,
        exchange: str,
        token: str,
    ) -> dict:

        signals = {}

        buy = 0
        sell = 0
        hold = 0

        for timeframe in cls.TIMEFRAMES:

            strategy = StrategyCache.get(
                exchange=exchange,
                token=token,
                timeframe=timeframe,
            )

            if strategy is None:

                signals[timeframe] = "UNKNOWN"
                continue

            signal = strategy["signal"]

            signals[timeframe] = signal

            if signal == "BUY":
                buy += 1

            elif signal == "SELL":
                sell += 1

            else:
                hold += 1

        #
        # Only count available timeframes
        #
        available = buy + sell + hold

        confirmation = 0

        if available > 0:

            confirmation = round(
                (max(buy, sell) / available) * 100
            )

        return {
            "signals": signals,
            "buy": buy,
            "sell": sell,
            "hold": hold,
            "available": available,
            "confirmation": confirmation,
        }