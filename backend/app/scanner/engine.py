from app.scanner.confidence_engine import ConfidenceEngine
from app.scanner.models import (
    IndicatorSnapshot,
    ScannerResult,
    TimeframeSignals,
)
from app.scanner.reason_builder import ReasonBuilder
from app.scanner.score_engine import ScoreEngine


class ScannerEngine:

    BUY = "BUY"

    WATCH = "WATCH"

    HOLD = "HOLD"

    @classmethod
    def scan(
        cls,
        *,
        exchange: str,
        symbol: str,
        token: str,
        indicators: IndicatorSnapshot,
        timeframes: TimeframeSignals,
    ) -> ScannerResult:

        score = ScoreEngine.calculate(
            indicators=indicators,
            timeframes=timeframes,
        )

        confidence = ConfidenceEngine.calculate(
            score=score,
            indicators=indicators,
            timeframes=timeframes,
        )

        reasons = ReasonBuilder.build(
            indicators=indicators,
            timeframes=timeframes,
        )

        recommendation = cls._recommendation(
            score=score,
            confidence=confidence,
        )

        return ScannerResult(
            exchange=exchange,
            symbol=symbol,
            token=token,
            score=score,
            confidence=confidence,
            recommendation=recommendation,
            reasons=reasons,
            indicators=indicators,
            timeframes=timeframes,
        )

    @classmethod
    def _recommendation(
        cls,
        *,
        score: int,
        confidence: int,
    ) -> str:

        if score >= 85 and confidence >= 85:
            return cls.BUY

        if score >= 65:
            return cls.WATCH

        return cls.HOLD