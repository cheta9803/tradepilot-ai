from app.risk.trailing import TrailingStop
from app.risk.breakeven import BreakEvenStop
from app.risk.limits import RiskLimits


class RiskEngine:

    @classmethod
    def process(
        cls,
        *,
        trade: dict,
        ltp: float,
    ) -> None:

        TrailingStop.process(
            trade=trade,
            ltp=ltp,
        )

        BreakEvenStop.process(
            trade=trade,
            ltp=ltp,
        )

        RiskLimits.process(
            trade=trade,
            ltp=ltp,
        )