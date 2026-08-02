from app.instruments.cache import InstrumentCache
from app.strategy.cache import StrategyCache
from app.trades.lifecycle import TradeLifecycle


class PaperTradingService:

    @staticmethod
    def create(
        exchange: str,
        token: str,
        timeframe: str,
    ) -> dict:

        instrument = InstrumentCache.get_by_token(
            token,
        )

        if instrument is None:
            raise ValueError(
                "Instrument not found.",
            )

        strategy = StrategyCache.get(
            exchange=exchange,
            token=token,
            timeframe=timeframe,
        )

        if strategy is None:
            raise ValueError(
                "Strategy not found.",
            )

        if not strategy["tradable"]:
            raise ValueError(
                "No tradable signal.",
            )

        TradeLifecycle.create(
            exchange=exchange,
            token=token,
            symbol=instrument.symbol,
            timeframe=timeframe,
            signal=strategy["signal"],
            state=strategy["state"],
            entry=strategy["entry"],
            stop_loss=strategy["stop_loss"],
            target=strategy["target"],
            quantity=strategy["quantity"],
            execution_mode="PAPER",
        )

        return {
            "message": "Paper trade created successfully.",
        }