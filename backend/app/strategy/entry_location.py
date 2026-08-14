from app.core.config import settings


class EntryLocationFilter:
    """Reject entries with insufficient room before nearby S/R.

    15m provides higher-timeframe context and 5m provides the immediate
    obstacle. The nearest valid level above a BUY entry (or below a SELL
    entry) is compared with the planned target plus a small volatility
    buffer.
    """

    TIMEFRAMES = ("5m", "15m")

    @classmethod
    def evaluate(
        cls,
        *,
        signal: str,
        entry: float,
        target: float,
        atr_5m: float,
        strategies: dict[str, dict],
    ) -> dict:
        if not settings.entry_location_filter_enabled:
            return cls._allow("Entry-location filter disabled.")

        if signal not in ("BUY", "SELL"):
            return cls._allow("No directional trade signal.")

        levels = []

        for timeframe in cls.TIMEFRAMES:
            strategy = strategies.get(timeframe) or {}

            pattern_timestamp = strategy.get("pattern_candle_timestamp")
            strategy_timestamp = strategy.get("candle_timestamp")

            if (
                pattern_timestamp
                and strategy_timestamp
                and pattern_timestamp != strategy_timestamp
            ):
                continue

            level = (
                strategy.get("resistance")
                if signal == "BUY"
                else strategy.get("support")
            )

            if level is None:
                continue

            level = float(level)

            if signal == "BUY" and level > entry:
                levels.append((level, timeframe))
            elif signal == "SELL" and level < entry:
                levels.append((level, timeframe))

        if not levels:
            return cls._allow(
                "No overhead resistance/support found in 5m/15m lookback."
            )

        if signal == "BUY":
            level, timeframe = min(levels, key=lambda item: item[0])
            room = level - entry
            target_distance = target - entry
            level_name = "resistance"
        else:
            level, timeframe = max(levels, key=lambda item: item[0])
            room = entry - level
            target_distance = entry - target
            level_name = "support"

        buffer = max(
            float(atr_5m or 0.0)
            * settings.entry_location_buffer_atr_multiplier,
            0.0,
        )
        required_room = target_distance + buffer

        if room < required_room:
            return {
                "allowed": False,
                "reason": (
                    f"Entry too close to {timeframe} {level_name}: "
                    f"room={room:.2f}, required={required_room:.2f}."
                ),
                "level": round(level, 2),
                "timeframe": timeframe,
                "room": round(room, 2),
                "required_room": round(required_room, 2),
            }

        return {
            "allowed": True,
            "reason": (
                f"Sufficient room to {timeframe} {level_name}: "
                f"room={room:.2f}."
            ),
            "level": round(level, 2),
            "timeframe": timeframe,
            "room": round(room, 2),
            "required_room": round(required_room, 2),
        }

    @staticmethod
    def _allow(reason: str) -> dict:
        return {
            "allowed": True,
            "reason": reason,
            "level": None,
            "timeframe": None,
            "room": None,
            "required_room": None,
        }
