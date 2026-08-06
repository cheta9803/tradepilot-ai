from app.ai.cache import AICache
from app.ai.scorer import AIScorer
from app.ai.timeframe_confirmation import TimeframeConfirmation
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

        confirmation = TimeframeConfirmation.calculate(
            exchange=exchange,
            token=token,
        )

        score = AIScorer.calculate(
            strategy=strategy,
            patterns=patterns,
        )

        #
        # Multi-timeframe confirmation
        #

        if confirmation["confirmation"] >= 75:

            score["score"] = min(
                score["score"] + 10,
                100,
            )

            score["confidence"] = score["score"]

            score["reasons"].append(
                f"Multi-timeframe confirmation ({confirmation['confirmation']}%)"
            )

        elif confirmation["confirmation"] < 40:

            score["score"] = max(
                score["score"] - 10,
                0,
            )

            score["confidence"] = score["score"]

            score["reasons"].append(
                f"Weak multi-timeframe confirmation ({confirmation['confirmation']}%)"
            )

        score["timeframes"] = confirmation["signals"]

        AICache.save(
            exchange=exchange,
            token=token,
            timeframe=timeframe,
            score=score,
        )