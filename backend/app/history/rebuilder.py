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

            candles_1m = HistoryCache.get(
                exchange=instrument.exchange,
                token=instrument.token,
                timeframe="1m",
            )

            if not candles_1m:
                continue

            for timeframe, interval in TIMEFRAMES.items():

                candles_tf = []

                for i in range(0, len(candles_1m), interval):

                    bucket = candles_1m[i:i + interval]

                    if len(bucket) != interval:
                        continue

                    candles_tf.append(
                        TimeframeBuilder.create_from_candles(
                            bucket,
                            timeframe,
                        )
                    )

                if not candles_tf:
                    continue

                HistoryCache.save(
                    exchange=instrument.exchange,
                    token=instrument.token,
                    timeframe=timeframe,
                    candles=candles_tf,
                )

                try:

                    IndicatorEngine.calculate(
                        symbol=instrument.symbol,
                        timeframe=timeframe,
                    )

                    StrategyEngine.calculate(
                        exchange=instrument.exchange,
                        token=instrument.token,
                        timeframe=timeframe,
                    )

                except Exception as e:

                    print(
                        f"Rebuild error "
                        f"{instrument.symbol} "
                        f"{timeframe}: {e}"
                    )

                print(
                    f"Rebuilt "
                    f"{instrument.symbol} "
                    f"{timeframe} "
                    f"{len(candles_tf)} candles"
                )