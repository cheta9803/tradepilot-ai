from app.indicators.cache import IndicatorCache
from app.trades.lifecycle import TradeLifecycle

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

        trailing_changed = TrailingStop.process(
            trade=trade,
            ltp=ltp,
            atr=atr,
        )

        #
        # TrailingStop persists its changes through
        # TradeLifecycle. Reload the latest trade state
        # before BreakEvenStop runs.
        #
        # This prevents BreakEvenStop from working with
        # an outdated stop_loss/highest_price/lowest_price.
        #
        if trailing_changed:

            latest_trade = TradeLifecycle.get(
                exchange=trade["exchange"],
                token=trade["token"],
                timeframe=trade["timeframe"],
            )

            if latest_trade is None:
                return

            trade = latest_trade

        BreakEvenStop.process(
            trade=trade,
            ltp=ltp,
            atr=atr,
        )