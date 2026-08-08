import json

from app.ai.scorer import AIScorer


class TimeframeConfirmation:
    @staticmethod
    def calculate(*args, **kwargs):
        from app.ai.timeframe_confirmation import TimeframeConfirmation as RealTimeframeConfirmation

        return RealTimeframeConfirmation.calculate(*args, **kwargs)


class PatternCache:
    @staticmethod
    def get(*args, **kwargs):
        from app.patterns.cache import PatternCache as RealPatternCache

        return RealPatternCache.get(*args, **kwargs)


class StrategyCache:
    @staticmethod
    def get(*args, **kwargs):
        from app.strategy.cache import StrategyCache as RealStrategyCache

        return RealStrategyCache.get(*args, **kwargs)


class AIService:

    @classmethod
    def top_opportunities(
        cls,
        *,
        timeframe: str = "1m",
        limit: int = 10,
    ) -> list[dict]:

        from app.db.redis import redis_client
        from app.instruments.cache import InstrumentCache

        opportunities = []

        for key in redis_client.scan_iter(match="strategy:*"):

            if isinstance(key, bytes):
                key = key.decode()

            _, exchange, token, strategy_timeframe = key.split(":")

            if strategy_timeframe != timeframe:
                continue

            strategy = StrategyCache.get(
                exchange=exchange,
                token=token,
                timeframe=strategy_timeframe,
            )

            if strategy is None:
                continue

            patterns = PatternCache.get(
                exchange=exchange,
                token=token,
                timeframe=strategy_timeframe,
            )

            confirmation = TimeframeConfirmation.calculate(
                exchange=exchange,
                token=token,
            )

            score = AIScorer.calculate(
                strategy=strategy,
                patterns=patterns,
            )

            if confirmation["confirmation"] >= 75:
                score["score"] = min(score["score"] + 10, 100)
                score["confidence"] = score["score"]
                score["reasons"].append(
                    f"Multi-timeframe confirmation ({confirmation['confirmation']}%)"
                )
            elif confirmation["confirmation"] < 40:
                score["score"] = max(score["score"] - 10, 0)
                score["confidence"] = score["score"]
                score["reasons"].append(
                    f"Weak multi-timeframe confirmation ({confirmation['confirmation']}%)"
                )

            score["timeframes"] = confirmation["signals"]

            instrument = InstrumentCache.get_by_token(token=token)

            if instrument is None:
                continue

            opportunities.append(
                {
                    "symbol": instrument.symbol,
                    "exchange": exchange,
                    "token": token,
                    **score,
                }
            )

        opportunities.sort(
            key=lambda x: (
                x.get("recommendation") == "NO SIGNAL",
                x.get("confidence", 0),
                x.get("score", 0),
                x.get("recommendation") != "BUY",
                x.get("recommendation") != "WATCH",
            ),
            reverse=False,
        )

        meaningful = [
            item for item in opportunities if item.get("recommendation") != "NO SIGNAL"
        ]

        if meaningful:
            return meaningful[:limit]

        return [
            {
                "symbol": None,
                "exchange": None,
                "token": None,
                "score": 0,
                "confidence": 0,
                "recommendation": "NO SIGNAL",
                "reasons": ["No strong signal available"],
                "timeframes": {},
            }
        ]