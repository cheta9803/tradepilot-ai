from datetime import datetime

from app.angel.client import AngelClient
from app.core.config import settings
from app.core.logger import logger
from app.trades.cache import TradeCache
from app.trades.lifecycle import TradeLifecycle


class OrderSyncService:

    @classmethod
    def sync_all(cls) -> None:

        if settings.paper_trading:

            logger.debug(
                "Order Sync skipped (paper trading enabled)"
            )

            return

        trades = TradeCache.get_all()

        for trade in trades:

            order_id = trade.get("order_id")

            if not order_id:
                continue

            cls.sync_trade(trade)

    @classmethod
    def sync_trade(
        cls,
        trade: dict,
    ) -> None:

        order = cls.fetch_order(
            trade["order_id"],
        )

        if order is None:
            return

        TradeLifecycle.update(
            exchange=trade["exchange"],
            token=trade["token"],
            timeframe=trade["timeframe"],
            values={
                "order_status": order["status"],
                "updated_at": datetime.now().isoformat(),
            },
        )

    @classmethod
    def fetch_order(
        cls,
        order_id: str,
    ) -> dict | None:

        try:

            smart_api = AngelClient.get_client()

            response = smart_api.orderBook()

            if response is None:
                return None

            if not response.get("status"):
                return None

            orders = response.get("data", [])

            for order in orders:

                if order.get("orderid") == order_id:

                    return {
                        "status": order.get(
                            "orderstatus",
                        ),
                    }

        except Exception:

            logger.exception(
                "Order synchronization failed."
            )

        return None