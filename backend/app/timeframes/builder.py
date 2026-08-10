from collections import defaultdict
from datetime import datetime

from app.candles.models import Candle


class TimeframeBuilder:

    @staticmethod
    def create_from_candles(
        candles: list[Candle],
        timeframe: str,
    ) -> Candle:

        if not candles:
            raise ValueError("No candles supplied.")

        candles = sorted(
            candles,
            key=lambda candle: candle.timestamp,
        )

        first = candles[0]
        last = candles[-1]

        return Candle(
            exchange=first.exchange,
            symbol=first.symbol,
            token=first.token,
            timeframe=timeframe,
            timestamp=first.timestamp,
            open=first.open,
            high=max(c.high for c in candles),
            low=min(c.low for c in candles),
            close=last.close,
            volume=sum(c.volume for c in candles),
        )

    @staticmethod
    def build_completed(
        candles: list[Candle],
        timeframe: str,
        interval: int,
    ) -> list[Candle]:

        if not candles:
            return []

        ordered = sorted(
            candles,
            key=lambda candle: candle.timestamp,
        )

        buckets: dict[datetime, dict[datetime, Candle]] = defaultdict(dict)

        for candle in ordered:
            bucket_start = TimeframeBuilder.bucket_start(
                candle.timestamp,
                interval,
            )
            minute = candle.timestamp.replace(
                second=0,
                microsecond=0,
            )
            buckets[bucket_start][minute] = candle

        result = []

        for bucket_start in sorted(buckets):
            bucket = buckets[bucket_start]

            # Never bridge an overnight/session boundary.
            if any(
                candle.timestamp.date() != bucket_start.date()
                for candle in bucket.values()
            ):
                continue

            if len(bucket) != interval:
                continue

            ordered_bucket = [
                bucket[timestamp]
                for timestamp in sorted(bucket)
            ]

            result.append(
                TimeframeBuilder.create_from_candles(
                    ordered_bucket,
                    timeframe,
                )
            )

        return result

    @staticmethod
    def bucket_start(
        timestamp: datetime,
        interval: int,
    ) -> datetime:

        minute = (
            timestamp.minute // interval
        ) * interval

        return timestamp.replace(
            minute=minute,
            second=0,
            microsecond=0,
        )
