from datetime import datetime
from zoneinfo import ZoneInfo

from app.candles.models import Candle


class VWAPCalculator:
    """Session VWAP using only candles from the latest trading session."""

    MARKET_TZ = ZoneInfo("Asia/Kolkata")

    @classmethod
    def _market_date(cls, timestamp: datetime):
        if timestamp.tzinfo is None:
            return timestamp.date()
        return timestamp.astimezone(cls.MARKET_TZ).date()

    @classmethod
    def calculate(cls, candles: list[Candle]) -> float | None:
        if not candles:
            return None

        latest_session = cls._market_date(candles[-1].timestamp)
        session_candles = [
            candle
            for candle in candles
            if cls._market_date(candle.timestamp) == latest_session
        ]

        cumulative_tp_volume = 0.0
        cumulative_volume = 0

        for candle in session_candles:
            if candle.volume <= 0:
                continue

            typical_price = (
                candle.high + candle.low + candle.close
            ) / 3

            cumulative_tp_volume += typical_price * candle.volume
            cumulative_volume += candle.volume

        if cumulative_volume == 0:
            return None

        return round(cumulative_tp_volume / cumulative_volume, 2)
