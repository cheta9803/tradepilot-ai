from app.candles.models import Candle


class TimeframeBuilder:

    @staticmethod
    def create_from_candles(
        candles: list[Candle],
        timeframe: str,
    ) -> Candle:

        if not candles:
            raise ValueError(
                "No candles supplied."
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
            volume=sum(
                c.volume
                for c in candles
            ),
        )