from app.history.redis_cache import HistoryCache
from app.indicators.engine import IndicatorEngine
from app.instruments.cache import InstrumentCache
from app.strategy.engine import StrategyEngine
from app.timeframes.builder import TimeframeBuilder
from app.timeframes.config import TIMEFRAMES


class HistoryRebuilder:

    @classmethod
    def rebuild(cls) -> None:

        instruments = InstrumentCache.get_all()

        for instrument in instruments:

            if instrument.exchange != "NSE":
                continue

            cls.rebuild_symbol(
                symbol=instrument.symbol,
            )

    @classmethod
    def rebuild_symbol(
        cls,
        *,
        symbol: str,
        timeframe: str | None = None,
    ) -> None:

        instrument = InstrumentCache.get_by_symbol(
            exchange="NSE",
            symbol=symbol,
        )

        if instrument is None:
            return

        candles_1m = HistoryCache.get(
            exchange=instrument.exchange,
            token=instrument.token,
            timeframe="1m",
        )

        if not candles_1m:
            return

        requested = (
            [timeframe]
            if timeframe
            else list(TIMEFRAMES.keys())
        )

        for current_timeframe in requested:

            if current_timeframe == "1m":

                try:

                    IndicatorEngine.calculate(
                        symbol=instrument.symbol,
                        timeframe="1m",
                    )

                except Exception as exc:

                    print(
                        f"Rebuild error "
                        f"{instrument.symbol} 1m: {exc}"
                    )

                continue

            interval = TIMEFRAMES.get(
                current_timeframe,
            )

            if interval is None:
                continue

            candles_tf = []

            for i in range(
                0,
                len(candles_1m),
                interval,
            ):

                bucket = candles_1m[
                    i:i + interval
                ]

                if len(bucket) != interval:
                    continue

                candles_tf.append(
                    TimeframeBuilder.create_from_candles(
                        bucket,
                        current_timeframe,
                    )
                )

            if not candles_tf:
                continue

            HistoryCache.save(
                exchange=instrument.exchange,
                token=instrument.token,
                timeframe=current_timeframe,
                candles=candles_tf,
            )

            try:

                IndicatorEngine.calculate(
                    symbol=instrument.symbol,
                    timeframe=current_timeframe,
                )

                StrategyEngine.calculate(
                    exchange=instrument.exchange,
                    token=instrument.token,
                    timeframe=current_timeframe,
                )

            except Exception as exc:

                print(
                    f"Rebuild error "
                    f"{instrument.symbol} "
                    f"{current_timeframe}: {exc}"
                )

            print(
                f"Rebuilt "
                f"{instrument.symbol} "
                f"{current_timeframe} "
                f"{len(candles_tf)} candles"
            )