from dataclasses import dataclass
from dataclasses import field
from datetime import datetime


@dataclass(slots=True)
class IndicatorSnapshot:

    trend: str = "UNKNOWN"

    trend_strength: int = 0

    ema20_above_ema50: bool = False

    price_above_ema20: bool = False

    rsi: float = 0.0

    macd_bullish: bool = False

    above_vwap: bool = False

    supertrend_buy: bool = False

    breakout: bool = False

    volume_spike: bool = False

    market_trend: str = "UNKNOWN"

    risk_reward: float = 0.0


@dataclass(slots=True)
class TimeframeSignals:

    one_minute: str = "UNKNOWN"

    five_minutes: str = "UNKNOWN"

    fifteen_minutes: str = "UNKNOWN"

    one_hour: str = "UNKNOWN"


@dataclass(slots=True)
class ScannerResult:

    exchange: str

    symbol: str

    token: str

    score: int

    confidence: int

    recommendation: str

    reasons: list[str] = field(
        default_factory=list,
    )

    indicators: IndicatorSnapshot = field(
        default_factory=IndicatorSnapshot,
    )

    timeframes: TimeframeSignals = field(
        default_factory=TimeframeSignals,
    )

    updated_at: datetime = field(
        default_factory=datetime.now,
    )