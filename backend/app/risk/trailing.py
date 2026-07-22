from app.core.config import settings
from app.trades.lifecycle import TradeLifecycle


class TrailingStop:

    @classmethod
    def process(
        cls,
        *,
        trade: dict,
        ltp: float,
        atr: float,
    ) -> None:

        if not settings.trailing_stop_enabled:
            return

        if atr <= 0:
            return

        state = trade["state"]

        if state == "BUY_ACTIVE":

            cls._process_buy(
                trade=trade,
                ltp=ltp,
                atr=atr,
            )

        elif state == "SELL_ACTIVE":

            cls._process_sell(
                trade=trade,
                ltp=ltp,
                atr=atr,
            )

    @classmethod
    def _process_buy(
        cls,
        *,
        trade: dict,
        ltp: float,
        atr: float,
    ) -> None:

        highest = max(
            trade.get(
                "highest_price",
                trade["entry_price"],
            ),
            ltp,
        )

        if highest <= trade.get(
            "highest_price",
            trade["entry_price"],
        ):
            return

        trailing_distance = (
            atr
            * settings.trailing_atr_multiplier
        )

        new_stop = highest - trailing_distance

        if (
            new_stop - trade["stop_loss"]
            < settings.min_stop_move
        ):
            return

        TradeLifecycle.update(
            exchange=trade["exchange"],
            token=trade["token"],
            timeframe=trade["timeframe"],
            values={
                "highest_price": highest,
                "stop_loss": round(new_stop, 2),
                "trail_started": True,
            },
        )

    @classmethod
    def _process_sell(
        cls,
        *,
        trade: dict,
        ltp: float,
        atr: float,
    ) -> None:

        lowest = min(
            trade.get(
                "lowest_price",
                trade["entry_price"],
            ),
            ltp,
        )

        if lowest >= trade.get(
            "lowest_price",
            trade["entry_price"],
        ):
            return

        trailing_distance = (
            atr
            * settings.trailing_atr_multiplier
        )

        new_stop = lowest + trailing_distance

        if (
            trade["stop_loss"] - new_stop
            < settings.min_stop_move
        ):
            return

        TradeLifecycle.update(
            exchange=trade["exchange"],
            token=trade["token"],
            timeframe=trade["timeframe"],
            values={
                "lowest_price": lowest,
                "stop_loss": round(new_stop, 2),
                "trail_started": True,
            },
        )