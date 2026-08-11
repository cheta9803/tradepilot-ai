from app.strategy.cache import StrategyCache
from app.strategy.risk import RiskManager


class MultiTimeframeStrategy:
    """Build one intraday trade decision from 15m, 5m and 1m strategy caches.

    15m = market bias
    5m  = setup + risk timeframe
    1m  = entry trigger
    """

    TIMEFRAMES = ("15m", "5m", "1m")

    WEIGHTS = {
        "15m": 0.40,
        "5m": 0.35,
        "1m": 0.25,
    }

    MIN_CONFIDENCE = 70

    @classmethod
    def calculate(
        cls,
        *,
        exchange: str,
        token: str,
    ) -> dict:
        strategies: dict[str, dict] = {}
        signals: dict[str, str] = {}
        confidences: dict[str, int] = {}

        for timeframe in cls.TIMEFRAMES:
            strategy = StrategyCache.get(
                exchange=exchange,
                token=token,
                timeframe=timeframe,
            )

            if strategy is None:
                signals[timeframe] = "UNKNOWN"
                continue

            strategies[timeframe] = strategy
            signals[timeframe] = strategy.get("signal", "HOLD")
            confidences[timeframe] = int(
                strategy.get("confidence", 0)
            )

        missing = [
            timeframe
            for timeframe in cls.TIMEFRAMES
            if timeframe not in strategies
        ]

        if missing:
            return cls._wait_result(
                signals=signals,
                confidences=confidences,
                reason=(
                    "Waiting for all timeframes: "
                    + ", ".join(missing)
                ),
            )

        direction = signals["15m"]

        if direction not in ("BUY", "SELL"):
            return cls._wait_result(
                signals=signals,
                confidences=confidences,
                reason="15m timeframe does not provide a trade direction.",
            )

        if any(
            signals[timeframe] != direction
            for timeframe in cls.TIMEFRAMES
        ):
            return cls._wait_result(
                signals=signals,
                confidences=confidences,
                reason="15m, 5m and 1m signals are not aligned.",
            )

        weak = [
            timeframe
            for timeframe in cls.TIMEFRAMES
            if confidences[timeframe] < cls.MIN_CONFIDENCE
        ]

        if weak:
            return cls._wait_result(
                signals=signals,
                confidences=confidences,
                reason=(
                    "Confidence below "
                    f"{cls.MIN_CONFIDENCE}% on "
                    + ", ".join(weak)
                ),
            )

        confidence = round(
            sum(
                confidences[timeframe] * cls.WEIGHTS[timeframe]
                for timeframe in cls.TIMEFRAMES
            )
        )

        entry_strategy = strategies["1m"]
        risk_strategy = strategies["5m"]

        entry = float(entry_strategy["entry"])
        atr_5m = float(risk_strategy["atr14"])

        stop_loss, target = RiskManager.calculate(
            signal=direction,
            entry=entry,
            atr=atr_5m,
        )

        reasons = [
            "15m bias aligned",
            "5m setup aligned",
            "1m entry trigger aligned",
            "Stop-loss based on 5m ATR",
            "Risk/reward = 1:2",
        ]

        return {
            "signal": direction,
            "recommendation": direction,
            "trade_ready": True,
            "confidence": min(confidence, 100),
            "signals": signals,
            "confidences": confidences,
            "entry": entry,
            "stop_loss": stop_loss,
            "target": target,
            "risk_reward": RiskManager.RISK_REWARD,
            "atr_5m": atr_5m,
            "reasons": reasons,
        }

    @staticmethod
    def _wait_result(
        *,
        signals: dict[str, str],
        confidences: dict[str, int],
        reason: str,
    ) -> dict:
        return {
            "signal": "HOLD",
            "recommendation": "WAIT",
            "trade_ready": False,
            "confidence": 0,
            "signals": signals,
            "confidences": confidences,
            "entry": None,
            "stop_loss": None,
            "target": None,
            "risk_reward": RiskManager.RISK_REWARD,
            "atr_5m": None,
            "reasons": [reason],
        }
