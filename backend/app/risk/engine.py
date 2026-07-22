from app.indicators.cache import IndicatorCache

from app.risk.breakeven import BreakEvenStop
from app.risk.trailing import TrailingStop


class RiskEngine:

    @classmethod
    def process(
        cls,
        *,
        trade: dict,
        ltp: float,
    ) -> None:

        indicators = IndicatorCache.get(
            exchange=trade["exchange"],
            token=trade["token"],
            timeframe=trade["timeframe"],
        )

        if indicators is None:
            return

        atr = indicators.get("atr14")

        if atr is None:
            return

        TrailingStop.process(
            trade=trade,
            ltp=ltp,
            atr=atr,
        )

        BreakEvenStop.process(
            trade=trade,
            ltp=ltp,
            atr=atr,
        )