from datetime import timedelta

from app.candles.models import Candle
from app.history.redis_cache import HistoryCache
from app.indicators.engine import IndicatorEngine
from app.timeframes.builder import TimeframeBuilder
from app.timeframes.config import TIMEFRAMES


class TimeframeAggregator:

    @classmethod
    def process(
        cls,
        candle: Candle,
    ) -> None:

        history_1m = HistoryCache.get(
            exchange=candle.exchange,
            token=candle.token,
            timeframe="1m",
        )

        if not history_1m:
            return

        completed = candle.timestamp - timedelta(minutes=1)

        for timeframe, interval in TIMEFRAMES.items():

            bucket_start = cls._bucket_start(
                completed,
                interval,
            )

            bucket_end = (
                bucket_start
                + timedelta(minutes=interval)
            )

            bucket = [
                c
                for c in history_1m
                if bucket_start <= c.timestamp < bucket_end
            ]

            if len(bucket) != interval:
                continue

            history = HistoryCache.get(
                exchange=candle.exchange,
                token=candle.token,
                timeframe=timeframe,
            )

            if (
                history
                and history[-1].timestamp == bucket_start
            ):
                continue

            try:

                candle_tf = (
                    TimeframeBuilder.create_from_candles(
                        bucket,
                        timeframe,
                    )
                )

                print(
                    f"Creating {timeframe} candle "
                    f"{candle_tf.timestamp}"
                )

                HistoryCache.append(candle_tf)

                IndicatorEngine.calculate(
                    symbol=candle.symbol,
                    timeframe=timeframe,
                )

                print(
                    f">>> New {timeframe} candle created "
                    f"{candle.symbol} "
                    f"{candle_tf.timestamp}"
                )

            except Exception as exc:
                import traceback

                traceback.print_exc()

    @staticmethod
    def _bucket_start(
        timestamp,
        interval,
    ):

        minute = (
            timestamp.minute // interval
        ) * interval

        return timestamp.replace(
            minute=minute,
            second=0,
            microsecond=0,
        )