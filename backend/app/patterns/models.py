from dataclasses import dataclass


@dataclass
class PatternResult:

    bullish_engulfing: bool = False

    bearish_engulfing: bool = False

    hammer: bool = False

    shooting_star: bool = False

    doji: bool = False

    morning_star: bool = False

    evening_star: bool = False

    breakout: bool = False

    breakdown: bool = False

    support: float | None = None

    resistance: float | None = None

    higher_high: bool = False

    lower_low: bool = False

    candle_timestamp: str | None = None
