from app.dashboard.constants import INDEX_SYMBOLS
from app.dashboard.mapper import DashboardMapper
from app.dashboard.models import DashboardResponse

from app.instruments.cache import InstrumentCache
from app.live.service import LiveService
from app.portfolio.service import PortfolioService
from app.trades.service import TradeService


class DashboardService:

    @classmethod
    def get(cls) -> DashboardResponse:

        portfolio = PortfolioService.summary()

        today_pnl = PortfolioService.today_pnl()

        positions = [
            DashboardMapper.position(trade)
            for trade in TradeService.get_open()
        ]

        orders = [
            DashboardMapper.order(trade)
            for trade in sorted(
                TradeService.get_all(),
                key=lambda trade: trade["updated_at"],
                reverse=True,
            )[:10]
        ]

        indices = []

        for exchange, symbol in INDEX_SYMBOLS:

            instrument = InstrumentCache.get_by_symbol(
                exchange=exchange,
                symbol=symbol,
            )

            live = None

            if instrument:
                live = LiveService.get(
                    instrument.token,
                )

            indices.append(
                DashboardMapper.market_index(
                    name=symbol,
                    live=live,
                )
            )

        return DashboardResponse(
            summary=DashboardMapper.summary(
                portfolio,
                today_pnl,
            ),
            indices=indices,
            positions=positions,
            orders=orders,
        )