from app.core.config import settings
from app.strategy.cache import StrategyCache
from app.strategy.entry_location import EntryLocationFilter
from app.strategy.risk import RiskManager


class MultiTimeframeStrategy:
    """Build one intraday trade decision from 15m, 5m and 1m strategy caches.

    15m = market bias
    5m  = setup + risk timeframe
    1m  = entry trigger

    The 1m timeframe must have an actual price-action trigger in addition
    to directional alignment. This prevents every aligned indicator state
    from becoming a new trade.
    """

    TIMEFRAMES = ("15m", "5m", "1m")

    WEIGHTS = {
        "15m": 0.40,
        "5m": 0.35,
        "1m": 0.25,
    }

    # V1 was too strict: requiring 75% on every timeframe produced almost
    # no executable trades. Keep strong alignment, but judge confidence at
    # the portfolio decision level instead of demanding 75% on each TF.
    MIN_CONFIDENCE = 70
    MIN_CONFIDENCE_BY_TIMEFRAME = {
        "15m": 65,
        "5m": 65,
        "1m": 70,
    }

    # 5m is the setup/risk timeframe, so do not allow a sub-70% setup even
    # though the general per-timeframe floor is intentionally lower. This
    # keeps the public hardening thresholds compatible while preventing a
    # 69% 5m setup from becoming executable merely because the 15m and 1m
    # scores are strong.
    MIN_5M_SETUP_CONFIDENCE = 70

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
            if confidences[timeframe] < cls.MIN_CONFIDENCE_BY_TIMEFRAME[timeframe]
        ]

        # The 5m timeframe is the actual setup/risk gate. Keep it at 70% or
        # better so a marginal setup cannot be rescued by strong 15m/1m
        # confidence.
        if confidences["5m"] < cls.MIN_5M_SETUP_CONFIDENCE and "5m" not in weak:
            weak.append("5m")

        if weak:
            details = ", ".join(
                f"{timeframe}={confidences[timeframe]}%"
                f"<{cls.MIN_CONFIDENCE_BY_TIMEFRAME[timeframe]}%"
                for timeframe in weak
            )
            return cls._wait_result(
                signals=signals,
                confidences=confidences,
                reason=f"Timeframe confidence too low: {details}",
            )

        entry_strategy = strategies["1m"]

        if not entry_strategy.get("entry_trigger", False):
            trigger_reason = entry_strategy.get(
                "entry_trigger_reason"
            )

            if trigger_reason:
                reason = (
                    "1m signal aligned, but entry trigger is not confirmed: "
                    f"{trigger_reason}"
                )
            else:
                reason = (
                    "1m signal aligned, but no fresh price-action "
                    "entry trigger is confirmed."
                )

            return cls._wait_result(
                signals=signals,
                confidences=confidences,
                reason=reason,
            )

        confidence = round(
            sum(
                confidences[timeframe] * cls.WEIGHTS[timeframe]
                for timeframe in cls.TIMEFRAMES
            )
        )

        if confidence < cls.MIN_CONFIDENCE:
            return cls._wait_result(
                signals=signals,
                confidences=confidences,
                reason=(
                    f"Weighted confidence {confidence}% is below "
                    f"{cls.MIN_CONFIDENCE}%."
                ),
            )

        risk_strategy = strategies["5m"]

        entry = float(entry_strategy["entry"])
        atr_5m = float(risk_strategy["atr14"])

        # Do not chase an already extended move. A valid breakout can still
        # be rejected if the live entry is materially away from the 5m mean.
        ema20_5m = risk_strategy.get("ema20")
        trigger_reason = entry_strategy.get("entry_trigger_reason") or ""
        is_breakout = "breakout" in trigger_reason.lower()
        max_chase_atr = (
            settings.no_chase_breakout_max_atr_from_ema20
            if is_breakout
            else settings.no_chase_max_atr_from_ema20
        )

        if (
            settings.no_chase_filter_enabled
            and ema20_5m is not None
            and atr_5m > 0
            and abs(entry - float(ema20_5m))
            > atr_5m * max_chase_atr
        ):
            return cls._wait_result(
                signals=signals,
                confidences=confidences,
                reason=(
                    "Entry rejected: price is too far from 5m EMA20 "
                    f"(limit={max_chase_atr:.2f} ATR) and the move is already extended."
                ),
            )

        stop_loss, target = RiskManager.calculate(
            signal=direction,
            entry=entry,
            atr=atr_5m,
        )

        location = EntryLocationFilter.evaluate(
            signal=direction,
            entry=entry,
            target=target,
            atr_5m=atr_5m,
            strategies=strategies,
        )

        if not location["allowed"]:
            return cls._wait_result(
                signals=signals,
                confidences=confidences,
                reason=location["reason"],
            )

        reasons = [
            "15m bias aligned",
            "5m setup aligned",
            "1m signal aligned",
            "1m price-action entry trigger confirmed",
            "Stop-loss based on 5m ATR",
            "Risk/reward = 1:2",
            location["reason"],
        ]

        if entry_strategy.get("entry_trigger_reason"):
            reasons.append(
                entry_strategy["entry_trigger_reason"]
            )

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
            "entry_trigger": True,
            "entry_trigger_reason": entry_strategy.get(
                "entry_trigger_reason"
            ),
            "entry_trigger_candle_timestamp": entry_strategy.get(
                "candle_timestamp"
            ),
            "location_filter": location,
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
            "entry_trigger": False,
            "entry_trigger_reason": None,
            "entry_trigger_candle_timestamp": None,
            "location_filter": None,
            "reasons": [reason],
        }
