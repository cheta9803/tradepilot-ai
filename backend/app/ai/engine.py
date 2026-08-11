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

        score = AIScorer.calculate(
            strategy=strategy,
            patterns=patterns,
        )

        confirmation = TimeframeConfirmation.calculate(
            exchange=exchange,
            token=token,
        )

        score["timeframes"] = confirmation["signals"]
        score["timeframe_confidences"] = confirmation["confidences"]

        # The 1m AI record is the master intraday decision consumed by the
        # scanner and AI opportunity list. Higher timeframes remain analytical.
        if timeframe == "1m":
            # The multi-timeframe confirmation is a TRADE-READINESS gate,
            # not a replacement for the underlying 1m AI analysis.
            #
            # When MTF is not ready, TimeframeConfirmation intentionally
            # returns confidence=0. If we copy that value into the AI score,
            # a perfectly valid 1m setup appears as 0/0 on the dashboard.
            # Preserve the base AIScorer result until all timeframes align.
            base_score = score["score"]
            base_confidence = score["confidence"]

            if confirmation["trade_ready"]:
                score["score"] = confirmation["confidence"]
                score["confidence"] = confirmation["confidence"]
                score["recommendation"] = confirmation["recommendation"]
            else:
                score["score"] = base_score
                score["confidence"] = base_confidence
                score["recommendation"] = "WAIT"

            score["direction"] = (
                confirmation["signal"]
                if confirmation["trade_ready"]
                else "NONE"
            )
            score["trade_ready"] = confirmation["trade_ready"]
            score["entry"] = confirmation["entry"]
            score["stop_loss"] = confirmation["stop_loss"]
            score["target"] = confirmation["target"]
            score["risk_reward"] = confirmation["risk_reward"]
            score["reasons"].extend(confirmation["reasons"])
        else:
            if confirmation["confirmation"] >= 75:
                score["score"] = min(score["score"] + 10, 100)
                score["confidence"] = score["score"]
                score["reasons"].append(
                    "Multi-timeframe confirmation "
                    f"({confirmation['confirmation']}%)"
                )
            elif confirmation["confirmation"] < 40:
                score["score"] = max(score["score"] - 10, 0)
                score["confidence"] = score["score"]
                score["reasons"].append(
                    "Weak multi-timeframe confirmation "
                    f"({confirmation['confirmation']}%)"
                )

        AICache.save(
            exchange=exchange,
            token=token,
            timeframe=timeframe,
            score=score,
        )
