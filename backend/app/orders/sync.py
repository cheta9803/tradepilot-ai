from datetime import datetime

from app.angel.client import AngelClient
from app.core.config import settings
from app.core.logger import logger
from app.core.market_session import MarketSession
from app.trades.lifecycle import TradeLifecycle
from app.trades.service import TradeService


class OrderSyncService:

    @classmethod
    def sync_all(cls) -> None:

        # ---------------------------------------------------------
        # Safety guard:
        #
        # Paper trading never communicates with the broker order book.
        # ---------------------------------------------------------

        if settings.paper_trading:

            logger.debug(
                "Broker order sync skipped: paper trading enabled."
            )

            return

        # ---------------------------------------------------------
        # Live trading must be explicitly enabled.
        # ---------------------------------------------------------

        if not settings.live_trading_enabled:

            logger.debug(
                "Broker order sync skipped: live trading disabled."
            )

            return

        # ---------------------------------------------------------
        # No reason to poll broker orders while the market is closed.
        # ---------------------------------------------------------

        if not MarketSession.is_open():

            logger.debug(
                "Broker order sync skipped: market is closed."
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

            order = orders.get(
                order_id
            )

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

        status = order["status"].upper()

        values = {
            "order_status": status,
            "updated_at": datetime.now().isoformat(),
        }

        average_price = order.get("average_price")

        if average_price is not None:
            values["entry_price"] = average_price
            values["current_price"] = average_price

        #
        # Order completely executed.
        #
        if status == "COMPLETE":

            values["state"] = (
                "BUY_ACTIVE"
                if trade["signal"] == "BUY"
                else "SELL_ACTIVE"
            )

        #
        # Still waiting at exchange.
        #
        elif status in (
            "PENDING",
            "OPEN",
            "TRIGGER PENDING",
        ):

            values["state"] = "ENTRY_READY"

        #
        # Broker rejected or failed order.
        #
        elif status in (
            "REJECTED",
            "FAILED",
        ):

            values.update(
                {
                    "state": "ENTRY_FAILED",
                    "reason": "Broker Order Failed",
                    "closed_at": datetime.now().isoformat(),
                }
            )

        #
        # Broker cancelled order.
        #
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
                logger.warning(
                    "Broker returned no response for order book."
                )
                return {}

            if not response.get("status"):
                logger.warning(
                    "Broker order book request failed: %s",
                    response,
                )
                return {}

            orders_data = response.get("data") or []

            if not isinstance(
                orders_data,
                list,
            ):
                logger.warning(
                    "Unexpected order book payload: %s",
                    response,
                )
                return {}

            orders: dict[str, dict] = {}

            for order in orders_data:

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