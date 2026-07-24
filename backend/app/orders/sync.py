from datetime import datetime

from app.angel.client import AngelClient
from app.core.config import settings
from app.core.logger import logger
from app.trades.lifecycle import TradeLifecycle
from app.trades.service import TradeService


class OrderSyncService:

    @classmethod
    def sync_all(cls) -> None:

        if settings.paper_trading:
            logger.debug(
                "Order Sync skipped (paper trading enabled)"
            )
            return

        trades = TradeService.get_open()

        if not trades:
            return

        orders = cls.fetch_orders()

        if not orders:
            return

        for trade in trades:

            order_id = trade.get("order_id")

            if not order_id:
                continue

            order = orders.get(order_id)

            if order is None:
                continue

            cls.sync_trade(
                trade=trade,
                order=order,
            )

    @classmethod
    def sync_trade(
        cls,
        trade: dict,
        order: dict,
    ) -> None:

        values = {
            "order_status": order["status"],
            "updated_at": datetime.now().isoformat(),
        }

        if order.get("average_price") is not None:
            values["entry_price"] = order[
                "average_price"
            ]

        status = order["status"].upper()

        if status == "REJECTED":

            values.update(
                {
                    "state": "REJECTED",
                    "reason": "Broker Rejected",
                    "closed_at": datetime.now().isoformat(),
                }
            )

        elif status == "CANCELLED":

            values.update(
                {
                    "state": "CANCELLED",
                    "reason": "Broker Cancelled",
                    "closed_at": datetime.now().isoformat(),
                }
            )

        TradeLifecycle.update(
            exchange=trade["exchange"],
            token=trade["token"],
            timeframe=trade["timeframe"],
            values=values,
        )

    @classmethod
    def fetch_orders(cls) -> dict[str, dict]:

        try:

            smart_api = AngelClient.get_client()

            response = smart_api.orderBook()

            if response is None:
                return {}

            if not response.get("status"):
                return {}

            orders = {}

            for order in response.get("data", []):

                order_id = order.get("orderid")

                if not order_id:
                    continue

                average_price = order.get(
                    "averageprice"
                )

                try:
                    average_price = (
                        float(average_price)
                        if average_price
                        else None
                    )
                except (
                    TypeError,
                    ValueError,
                ):
                    average_price = None

                orders[order_id] = {
                    "status": order.get(
                        "orderstatus",
                        "",
                    ),
                    "average_price": average_price,
                    "filled_quantity": order.get(
                        "filledshares"
                    ),
                    "pending_quantity": order.get(
                        "unfilledshares"
                    ),
                }

            logger.info(
                "Fetched %d broker orders from broker.",
                len(orders),
            )

            return orders

        except Exception:

            logger.exception(
                "Order synchronization failed."
            )

            return {}