from app.strategy.multi_timeframe import MultiTimeframeStrategy


class TimeframeConfirmation:
    """Compatibility facade for the AI layer."""

    TIMEFRAMES = list(MultiTimeframeStrategy.TIMEFRAMES)

    @classmethod
    def calculate(
        cls,
        *,
        exchange: str,
        token: str,
    ) -> dict:
        decision = MultiTimeframeStrategy.calculate(
            exchange=exchange,
            token=token,
        )

        signals = decision["signals"]
        buy = sum(1 for signal in signals.values() if signal == "BUY")
        sell = sum(1 for signal in signals.values() if signal == "SELL")
        hold = sum(
            1
            for signal in signals.values()
            if signal not in ("BUY", "SELL", "UNKNOWN")
        )
        available = sum(
            1 for signal in signals.values() if signal != "UNKNOWN"
        )

        return {
            **decision,
            "buy": buy,
            "sell": sell,
            "hold": hold,
            "available": available,
            "confirmation": decision["confidence"] if decision["trade_ready"] else 0,
        }
