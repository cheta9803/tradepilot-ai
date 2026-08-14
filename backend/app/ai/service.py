from app.ai.scorer import AIScorer
from app.db.redis import redis_client
from app.instruments.cache import InstrumentCache
from app.ai.timeframe_confirmation import TimeframeConfirmation
from app.patterns.cache import PatternCache
from app.strategy.cache import StrategyCache
from app.strategy.execution_eligibility import TradeExecutionEligibility


class AIService:

    @classmethod
    def top_opportunities(
        cls,
        *,
        timeframe: str = "1m",
        limit: int = 10,
    ) -> list[dict]:
        opportunities: list[dict] = []
        seen: set[tuple[str, str]] = set()

        for key in redis_client.scan_iter(match="strategy:*:1m"):
            if isinstance(key, bytes):
                key = key.decode()

            parts = key.split(":")
            if len(parts) != 4:
                continue

            _, exchange, token, strategy_timeframe = parts

            if strategy_timeframe != timeframe:
                continue

            identity = (exchange, token)
            if identity in seen:
                continue
            seen.add(identity)

            strategy = StrategyCache.get(
                exchange=exchange,
                token=token,
                timeframe="1m",
            )
            if strategy is None:
                continue

            confirmation = TimeframeConfirmation.calculate(
                exchange=exchange,
                token=token,
            )

            patterns = PatternCache.get(
                exchange=exchange,
                token=token,
                timeframe="1m",
            )

            score = AIScorer.calculate(
                strategy=strategy,
                patterns=patterns,
            )

            master_ready = confirmation["trade_ready"]
            master_signal = confirmation["signal"]

            if master_ready:
                # Once all timeframes are aligned, the MTF confidence is the
                # final trade confidence.
                score["recommendation"] = master_signal
                score["confidence"] = confirmation["confidence"]
                score["score"] = confirmation["confidence"]
            else:
                # MTF confirmation is a trade-readiness gate. A WAIT result
                # must not erase the useful underlying 1m AI score.
                # TimeframeConfirmation returns confidence=0 while waiting,
                # which previously caused every WAIT opportunity to display
                # 0 score / 0 confidence.
                score["recommendation"] = "WAIT"

            score["reasons"].extend(
                confirmation["reasons"]
            )

            score["direction"] = (
                master_signal
                if master_ready
                else "NONE"
            )
            score["trade_ready"] = master_ready

            execution_ready = False
            execution_block_reason = None

            if master_ready:
                eligibility = TradeExecutionEligibility.evaluate(
                    exchange=exchange,
                    token=token,
                    trigger_candle_timestamp=confirmation.get(
                        "entry_trigger_candle_timestamp"
                    ),
                )
                execution_ready = eligibility["execution_ready"]
                execution_block_reason = eligibility[
                    "execution_block_reason"
                ]

            score["execution_ready"] = execution_ready
            score["execution_block_reason"] = execution_block_reason

            if execution_block_reason:
                score["reasons"].append(
                    f"Execution blocked: {execution_block_reason}"
                )

            score["timeframes"] = confirmation["signals"]
            score["timeframe_confidences"] = confirmation[
                "confidences"
            ]
            score["entry"] = confirmation["entry"]
            score["stop_loss"] = confirmation["stop_loss"]
            score["target"] = confirmation["target"]
            score["risk_reward"] = confirmation["risk_reward"]

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
            key=lambda item: (
                not item.get("trade_ready", False),
                -item.get("confidence", 0),
                -item.get("score", 0),
            )
        )

        if opportunities:
            return opportunities[:limit]

        return [
            {
                "symbol": None,
                "exchange": None,
                "token": None,
                "score": 0,
                "confidence": 0,
                "recommendation": "NO SIGNAL",
                "direction": "NONE",
                "trade_ready": False,
                "execution_ready": False,
                "execution_block_reason": "No strategy data available",
                "reasons": ["No strategy data available"],
                "timeframes": {},
            }
        ]
