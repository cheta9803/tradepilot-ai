from datetime import datetime

from app.core.config import settings
from app.orders.enums import OrderStatus
from app.smartapi.client import smart_api
from app.trades.cache import TradeCache
from app.trades.lifecycle import TradeLifecycle


class OrderSyncService:

    @classmethod
    def sync_all(cls) -> None:

        if settings.paper_trading:

            from datetime import datetime

            print(
                f"[{datetime.now().strftime('%H:%M:%S')}] Order Sync skipped (paper trading enabled)"
            )

            return

        trades = TradeCache.get_all()

        for trade in trades:

            order_id = trade.get("order_id")

            if not order_id:
                continue

            cls.sync_trade(trade)

    @classmethod
    def sync_trade(cls, trade: dict) -> None:

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

            response = smart_api.orderBook()

            if not response.get("status"):
                return None

            orders = response["data"]

            for order in orders:

                if order["orderid"] == order_id:

                    return {
                        "status": order["orderstatus"],
                    }

        except Exception as e:

            print(
                f"Order Sync Error: {e}"
            )

        return None