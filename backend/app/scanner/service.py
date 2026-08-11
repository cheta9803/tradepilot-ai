from datetime import datetime

from app.ai.cache import AICache
from app.core.market_session import MarketSession
from app.instruments.cache import InstrumentCache
from app.patterns.cache import PatternCache
from app.scanner.models import (
    IndicatorSnapshot,
    ScannerResult,
    TimeframeSignals,
)
from app.scanner.redis_cache import ScannerCache
from app.scanner.universe import Nifty50Universe
from app.strategy.cache import StrategyCache


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

            strategy = StrategyCache.get(
                exchange=instrument.exchange,
                token=instrument.token,
                timeframe=cls.TIMEFRAME,
            )

            if strategy is None:
                continue

            patterns = PatternCache.get(
                exchange=instrument.exchange,
                token=instrument.token,
                timeframe=cls.TIMEFRAME,
            )

            result = cls._build_result(
                instrument=instrument,
                ai_score=ai_score,
                strategy=strategy,
                patterns=patterns,
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
        strategy: dict,
        patterns: dict | None,
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

        indicators = cls._build_indicators(
            strategy=strategy,
            patterns=patterns,
        )

        updated_at = cls._parse_updated_at(
            strategy.get(
                "updated_at",
            )
            or ai_score.get(
                "updated_at",
            )
        )

        market_status = (
            MarketSession.status()
        )

        data_status = (
            MarketSession.data_status(
                updated_at,
            )
        )

        data_age_seconds = (
            MarketSession.data_age_seconds(
                updated_at,
            )
        )

        recommendations_available = (
            market_status == "OPEN"
            and data_status == "LIVE"
        )

        return ScannerResult(
            exchange=instrument.exchange,
            symbol=instrument.symbol,
            token=instrument.token,
            score=score,
            confidence=confidence,
            recommendation=recommendation,
            direction=ai_score.get(
                "direction",
                "NONE",
            ),
            trade_ready=bool(
                ai_score.get(
                    "trade_ready",
                    False,
                )
            ),
            entry=ai_score.get("entry"),
            stop_loss=ai_score.get("stop_loss"),
            target=ai_score.get("target"),
            risk_reward=float(
                ai_score.get(
                    "risk_reward",
                    strategy.get("risk_reward", 0.0),
                )
            ),
            reasons=reasons,
            indicators=indicators,
            timeframes=timeframes,
            updated_at=updated_at,
            market_status=market_status,
            data_status=data_status,
            data_age_seconds=round(
                data_age_seconds,
                2,
            ),
            recommendations_available=(
                recommendations_available
            ),
        )

    @staticmethod
    def _build_indicators(
        *,
        strategy: dict,
        patterns: dict | None,
    ) -> IndicatorSnapshot:

        trend = strategy.get(
            "trend",
            "UNKNOWN",
        )

        if trend == "UPTREND":

            normalized_trend = "UP"

        elif trend == "DOWNTREND":

            normalized_trend = "DOWN"

        else:

            normalized_trend = "UNKNOWN"

        entry = float(
            strategy.get(
                "entry",
                0.0,
            )
        )

        ema20 = float(
            strategy.get(
                "ema20",
                0.0,
            )
        )

        ema50 = float(
            strategy.get(
                "ema50",
                0.0,
            )
        )

        rsi = float(
            strategy.get(
                "rsi14",
                0.0,
            )
        )

        macd = float(
            strategy.get(
                "macd",
                0.0,
            )
        )

        signal_line = float(
            strategy.get(
                "signal_line",
                0.0,
            )
        )

        vwap = strategy.get(
            "vwap",
        )

        supertrend_signal = strategy.get(
            "supertrend_signal",
            "UNKNOWN",
        )

        breakout = bool(
            patterns
            and patterns.get(
                "breakout",
                False,
            )
        )

        volume_spike = bool(
            patterns
            and patterns.get(
                "volume_spike",
                False,
            )
        )

        return IndicatorSnapshot(
            trend=normalized_trend,

            trend_strength=0,

            ema20_above_ema50=(
                ema20 > ema50
            ),

            price_above_ema20=(
                entry > ema20
            ),

            rsi=rsi,

            macd_bullish=(
                macd > signal_line
            ),

            above_vwap=(
                vwap is not None
                and entry > float(vwap)
            ),

            supertrend_buy=(
                supertrend_signal == "BUY"
            ),

            breakout=breakout,

            volume_spike=volume_spike,

            market_trend="UNKNOWN",

            risk_reward=float(
                strategy.get(
                    "risk_reward",
                    0.0,
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

            return MarketSession.now()

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

            return MarketSession.now()

    @classmethod
    def get_top(
        cls,
        *,
        limit: int = DEFAULT_LIMIT,
        refresh: bool = False,
    ) -> list[dict]:

        if refresh:

            cls.scan_market(
                limit=limit,
            )

        results = ScannerCache.get_top()

        return results[:limit]