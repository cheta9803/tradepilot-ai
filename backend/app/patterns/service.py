from app.patterns.breakout import (
    BreakoutDetector,
)
from app.patterns.candlestick import (
    CandlestickPatternDetector,
)
from app.patterns.models import (
    PatternResult,
)
from app.patterns.support_resistance import (
    SupportResistanceDetector,
)


class PatternService:

    @classmethod
    def analyze(
        cls,
        candles,
    ) -> PatternResult:

        result = (
            CandlestickPatternDetector.detect(
                candles
            )
        )

        (
            result.support,
            result.resistance,
        ) = (
            SupportResistanceDetector.detect(
                candles
            )
        )

        (
            result.breakout,
            result.breakdown,
        ) = (
            BreakoutDetector.detect(
                candles
            )
        )

        return result