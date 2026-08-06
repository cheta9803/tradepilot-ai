from app.ai.cache import AICache
from app.ai.scorer import AIScorer
from app.patterns.cache import PatternCache
from app.strategy.cache import StrategyCache


class AIEngine:

    @classmethod
    def calculate(
        cls,
        *,
        exchange: str,
        token: str,
        timeframe: str,
    ) -> None:

        strategy = StrategyCache.get(
            exchange=exchange,
            token=token,
            timeframe=timeframe,
        )

        if strategy is None:
            return

        patterns = PatternCache.get(
            exchange=exchange,
            token=token,
            timeframe=timeframe,
        )

        score = AIScorer.calculate(
            strategy=strategy,
            patterns=patterns,
        )

        AICache.save(
            exchange=exchange,
            token=token,
            timeframe=timeframe,
            score=score,
        )