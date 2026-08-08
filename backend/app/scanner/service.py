from datetime import datetime

from app.ai.cache import AICache
from app.instruments.cache import InstrumentCache
from app.scanner.models import (
    IndicatorSnapshot,
    ScannerResult,
    TimeframeSignals,
)
from app.scanner.redis_cache import ScannerCache
from app.scanner.universe import Nifty50Universe


class ScannerService:

    TIMEFRAME = "1m"

    DEFAULT_LIMIT = 10

    @classmethod
    def scan_market(
        cls,
        *,
        limit: int = DEFAULT_LIMIT,
    ) -> list[ScannerResult]:

        results: list[ScannerResult] = []

        for instrument in InstrumentCache.get_all():

            if instrument.exchange != "NSE":
                continue

            if not Nifty50Universe.contains(
                instrument.symbol,
            ):
                continue

            ai_score = AICache.get(
                exchange=instrument.exchange,
                token=instrument.token,
                timeframe=cls.TIMEFRAME,
            )

            if ai_score is None:
                continue

            result = cls._build_result(
                instrument=instrument,
                ai_score=ai_score,
            )

            results.append(
                result,
            )

        results.sort(
            key=lambda result: (
                result.score,
                result.confidence,
            ),
            reverse=True,
        )

        results = results[:limit]

        ScannerCache.save_top(
            results,
        )

        for result in results:
            ScannerCache.save(
                result,
            )

        return results

    @classmethod
    def _build_result(
        cls,
        *,
        instrument,
        ai_score: dict,
    ) -> ScannerResult:

        score = int(
            ai_score.get(
                "score",
                0,
            )
        )

        confidence = int(
            ai_score.get(
                "confidence",
                score,
            )
        )

        recommendation = ai_score.get(
            "recommendation",
            "NO SIGNAL",
        )

        reasons = list(
            ai_score.get(
                "reasons",
                [],
            )
        )

        timeframes = cls._build_timeframes(
            ai_score.get(
                "timeframes",
                {},
            )
        )

        return ScannerResult(
            exchange=instrument.exchange,
            symbol=instrument.symbol,
            token=instrument.token,
            score=score,
            confidence=confidence,
            recommendation=recommendation,
            reasons=reasons,
            indicators=IndicatorSnapshot(),
            timeframes=timeframes,
            updated_at=cls._parse_updated_at(
                ai_score.get(
                    "updated_at",
                )
            ),
        )

    @staticmethod
    def _build_timeframes(
        values: dict,
    ) -> TimeframeSignals:

        return TimeframeSignals(
            one_minute=values.get(
                "1m",
                "UNKNOWN",
            ),
            five_minutes=values.get(
                "5m",
                "UNKNOWN",
            ),
            fifteen_minutes=values.get(
                "15m",
                "UNKNOWN",
            ),
            one_hour=values.get(
                "1h",
                "UNKNOWN",
            ),
        )

    @staticmethod
    def _parse_updated_at(
        value,
    ) -> datetime:

        if not value:
            return datetime.now()

        if isinstance(
            value,
            datetime,
        ):
            return value

        try:
            return datetime.fromisoformat(
                value,
            )
        except (
            TypeError,
            ValueError,
        ):
            return datetime.now()

    @classmethod
    def get_top(
        cls,
        *,
        limit: int = DEFAULT_LIMIT,
    ) -> list[dict]:

        results = ScannerCache.get_top()

        return results[:limit]